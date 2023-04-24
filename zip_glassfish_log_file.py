import os
import zipfile
from datetime import datetime


def archive_glassfish_logs(log_path):
    zip_files = {}
    for file in os.listdir(log_path):
        if file.startswith('server.log_'):
            file_date_str = file.split('server.log_')[1].split('.')[0]
            file_date = datetime.strptime(file_date_str, '%Y-%m-%dT%H-%M-%S')
            zip_name = file_date.strftime('%Y-%m') + '.zip'
            if zip_name not in zip_files:
                zip_files[zip_name] = []
            zip_files[zip_name].append(file)
    # Add a timestamp to zip (do not override zip)
    for zip_name, files in zip_files.items():
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        new_zip_name = zip_name.replace('.zip', '_timestamp_' + timestamp + '.zip')
        with zipfile.ZipFile(os.path.join(log_path, new_zip_name), 'a') as log_zip:
            for file in files:
                log_zip.write(os.path.join(log_path, file), file)
                os.remove(os.path.join(log_path, file))


archive_glassfish_logs("./logs") # GlassFish 4.1.2 log directory
