#!/usr/bin/python3

import sys
from datetime import datetime
from os import walk
from os import path
import zipfile
import re

def zipdir(directory_path, ziph):
    for root, dirs, files in walk(directory_path):
        for file in files:
            ziph.write(path.join(root, file), path.relpath(path.join(root, file), path.join(directory_path, '..')))

def create_backup_zip_file_name(source_folder):
    time_stamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    folder_base_path = re.sub('/$', '', source_folder)
    dir_name = path.basename(folder_base_path)
    return dir_name + "_" + str(time_stamp) + "_backup.zip"

if len(sys.argv) != 3:
    print("Missing target and/or destination folder")
    exit(1)

source_folder = sys.argv[1]
target_folder = sys.argv[2]

if not path.exists(source_folder):
    print("source folder does not exist")
    exit(1)

if not path.exists(target_folder):
    print("target folder does not exist")
    exit(1)

backup_file_path = path.join(target_folder, create_backup_zip_file_name(source_folder))

zipf = zipfile.ZipFile(backup_file_path, 'w', zipfile.ZIP_DEFLATED)
zipdir(source_folder, zipf)
zipf.close()
