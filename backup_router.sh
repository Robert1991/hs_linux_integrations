#!/bin/bash

# cleaning old backups
echo "Will delete old backups:"
find /media/extern/backups/router/ -mindepth 1 -mtime +5 -print
find /media/extern/backups/router/ -mindepth 1 -mtime +5 -delete

time_stamp=$(date +%d-%b-%H_%M)    
command_line="umask go= && sysupgrade -b /tmp/backup-RPNRouter-$time_stamp.tar.gz"

ssh root@RPNRouter $command_line
scp root@RPNRouter:"/tmp/backup-RPNRouter-$time_stamp.tar.gz" /media/extern/backups/router/