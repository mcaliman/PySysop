# PySysop

## restore_remote_database.py
Example of use
```
from restore_remote_database import RestoreRemoteDatabase
server = "myserver.ext"
username = "mcaliman"
password = "superpass"
dbName = "mydb"
dbUser = "user"
dbPass = "mysecret"
dump = RestoreRemoteDatabase(server, username, password, 22, dbName, dbUser, dbPass, verbose=False)
dump.execute() 
```