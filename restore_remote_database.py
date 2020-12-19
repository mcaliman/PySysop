import gzip
import os.path
import shutil
import subprocess
import time

import paramiko
from paramiko import SSHException, AuthenticationException, BadHostKeyException


class RestoreRemoteDatabase(object):
    """
    Connect to remote server with ssh protocol, create zipped dump, download and restore to localhost
    developed for MySql database, parameterization easy for other databases
    """

    def __init__(self, ssh_server, ssh_user, ssh_password, port, db_name, db_user, db_password, verbose=False):
        self.ssh_server = ssh_server
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.port = port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.verbose = verbose

        self.dump_command = '/usr/local/mysql/bin/mysqldump -u %s -p%s --opt --routines %s| /bin/gzip > %s'
        self.delete_command = 'rm %s'

        timestap = str(int(time.time()))
        self.remote_backup_filename = '%s_dump.sql.zip' % timestap
        self.local_backup_filename = '%s.sql.zip' % self.db_name
        self.local_dump_filename = '%s.sql' % self.db_name

        self.restore_script_filename = "%s_restore.sql" % self.db_name

        self.restore_sql_script = """ 
            drop database if exists {0};
            create database {0};
            use {0};
            set autocommit = 0;
            set foreign_key_checks = 0;
            SET character_set_client = 'utf8mb4';
            SET character_set_connection = 'utf8mb4';
            SET collation_connection = 'utf8mb4_unicode_ci';
            source {0}.sql;
            set foreign_key_checks = 1;
            commit;
            set autocommit = 1;
        """

        self.restore_command = "mysql -uroot -ppassword  <  %s"
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


    def __verbose(self, text):
        if self.verbose:
            print(text)

    def connect(self):
        """
        Connect via SSH to remote host
        """
        try:
            self.ssh.connect(self.ssh_server, username=self.ssh_user, password=self.ssh_password)
        except AuthenticationException as authenticationException:
            print("Authentication failed, please verify your credentials: %s" % authenticationException)
            exit()
        except SSHException as sshException:
            print("Unable to establish SSH connection: %s" % sshException)
            exit()
        except BadHostKeyException as badHostKeyException:
            print("Unable to verify server's host key: %s" % badHostKeyException)
            exit()

    def disconnect(self):
        """
        Disconnect from remote host
        """
        self.ssh.close()
        self.__verbose("Remote connection closed. Bye Bye")

    def execute_command(self, cmd):
        """
        Exceute remote command
        :param cmd: the command to execute
        """
        self.__verbose("Exceute remote command: %s" % cmd)
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd)
        self.__verbose(ssh_stdout.readlines())
        self.__verbose(ssh_stderr.readlines())

    def create(self):
        """
        Create database dump
        """
        cmd = self.dump_command % (self.db_user, self.db_password, self.db_name, self.remote_backup_filename)
        self.execute_command(cmd)

    def download(self):
        """
        Download the zipped backup file
        """
        transport = paramiko.Transport(self.ssh_server, self.port)
        transport.connect(username=self.ssh_user, password=self.ssh_password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(self.remote_backup_filename, self.local_backup_filename)
        sftp.close
        transport.close()
        #
        self.__cleanup_remotehost()

    def __cleanup_remotehost(self):
        cmd = self.delete_command % self.remote_backup_filename
        self.__verbose("Exceute command: %s" % cmd)
        self.execute_command(cmd)

    def __unzip(self):
        zipped = self.local_backup_filename
        unzipped = self.local_dump_filename
        self.__verbose("Unzip %s to %s" % (zipped, unzipped))
        with gzip.open(zipped, 'rb') as fin:
            with open(unzipped, 'wb') as fout:
                shutil.copyfileobj(fin, fout)

    def __cleanup_localhost(self):
        os.remove(self.local_backup_filename)
        os.remove(self.local_dump_filename)
        os.remove(self.restore_script_filename)

    def restore(self):
        self.__unzip()
        restore_sql_script_content = self.restore_sql_script.format(self.db_name)
        self.__verbose(restore_sql_script_content)
        file = open(self.restore_script_filename, "w+")
        file.write(restore_sql_script_content)
        file.close()

        cmd = self.restore_command % self.restore_script_filename
        self.__verbose(cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            self.__verbose(line),
        retval = p.wait()
        self.__verbose("retval %s" % retval)
        self.__cleanup_localhost()

    def execute(self):
        self.connect()
        self.create()
        self.download()
        self.disconnect()
        self.restore()

