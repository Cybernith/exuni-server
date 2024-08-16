#/bin/bash

files="/tmp/rclone/crypt"
path="sobhan-backups/$(date -u +%Y/%m/%d/%T)"

echo "backuping postgres..."
pg_dumpall | gzip > backup.gz

echo "encrypting..."
rclone copy backup.gz crypt:

echo "copying to sobhan google drive..."
rclone copy $files sobhan-gmail:$path

echo "copying to mmd google drive..."
rclone copy $files drive:$path

echo "copying to dropbox..."
rclone copy $files dropbox:$path

echo "copying to mega..."
rclone copy $files mega:$path

echo "removing encrypted files..."
rm -rf $files
