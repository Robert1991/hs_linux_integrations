#!/usr/bin/python3

import sys
from datetime import datetime
from os import walk
from os import path
from os import listdir
from os import stat
from os import remove
import zipfile
import re
import sys, getopt
import time


def delete_files_in_folder_older_than(folder_path, days = 4):
    now = time.time()
    for file in listdir(folder_path):
        full_file_path = path.join(folder_path, file)
        if stat(full_file_path).st_mtime < now - days * 86400:
            if path.isfile(full_file_path):
                print("deleting: " + full_file_path)
                remove(full_file_path)

def zipdir(directory_path, ziph):
    for root, dirs, files in walk(directory_path):
        for file in files:
            try:
                ziph.write(path.join(root, file), path.relpath(path.join(root, file), path.join(directory_path, '..')))
            except:
                print("Unexpected error:", sys.exc_info()[0])


def create_backup_zip_file_name(source_folder):
    time_stamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    folder_base_path = re.sub('/$', '', source_folder)
    dir_name = path.basename(folder_base_path)
    return dir_name + "_" + str(time_stamp) + "_backup.zip"

def usage():
    print("usage: backup_folder.py -c <opt:cleanup files in folder older than x days> -i <input_folder> -o <output_folder>")

try:
    if len(sys.argv) > 1:
        opts, args = getopt.getopt(sys.argv[1:],"c:i:o:")
    else:
        usage()
        sys.exit(2)        
except getopt.GetoptError as err:
    usage()
    print(err)
    sys.exit(2)

clean_up_folder = False
days = 0
source_folder = None
target_folder = None

for opt, arg in opts:
    if opt == "-c":
        clean_up_folder = True
        days = int(arg)
    elif opt == "-i":
        source_folder = arg
    elif opt == "-o":
        target_folder = arg
    elif opt == "-h":
        usage()
        exit(2)

if not path.exists(source_folder):
    print("source folder does not exist")
    exit(1)

if not path.exists(target_folder):
    print("target folder does not exist")
    exit(1)

backup_file_path = path.join(target_folder, create_backup_zip_file_name(source_folder))

print("Begin creating backup at: " + backup_file_path)
zipf = zipfile.ZipFile(backup_file_path, 'w', zipfile.ZIP_DEFLATED)
zipdir(source_folder, zipf)
zipf.close()
print("Backup created at: " + backup_file_path)

if clean_up_folder:
    print("Cleaning up backups older than " + str(days) + " days")
    delete_files_in_folder_older_than(target_folder, days)
