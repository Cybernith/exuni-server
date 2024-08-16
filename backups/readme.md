## Backups
This folder holds backups for commands. Database backup will run using postgres-backup.sh script

## Restore backups
### To decrypt backup:
1. Download [rclone](https://rclone.org/downloads/) if you don't have it
2. Download encrypted file to project directory (don't rename it)
3. In `rclone.conf` change `remote` to project directory 
4. Run `.\rclone.exe copy crypt: local:`
5. `backup.gz` will appear in project directory, it contains a `backup` file, decompress it into project directory

### To Restore backup (windows)
1. Create a database and user
2. Go to `[postgres install folder]/bin`
3. Run `psql.exe -U [user name] -d [database name] -f [project directory]\backup`
5. For myself:
    1. `cd C:\Program Files\PostgreSQL\13\bin`
    2. `psql.exe -U postgres -d sobhan -f D:\sobhanHesab\server\backup`

