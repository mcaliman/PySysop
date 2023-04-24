import os
import shutil
from pathlib import Path
from datetime import datetime

now = datetime.now()
timestamp = now.strftime('%Y%m%d%H%M%S')

shared_drive = "U:\\Phobos7"

backup_folder = Path(shared_drive) / "Backup" / timestamp

if not backup_folder.exists():
    backup_folder.mkdir()

username = os.getlogin()

folders_to_copy = ["Desktop", "Documents", "Pictures", "Music", "github", "IdeaProjects"]

for folder in folders_to_copy:
    print("copy...")
    source_folder = Path.home() / folder
    destination_folder = backup_folder / folder
    print("source_folder ", source_folder)
    print("destination_folder ", destination_folder)
    shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)
print("End! Bye Bye.")
