#!/bin/sh

set +x

LOG_LOCATION="/root/backup-wp/log"

# sauvegarde des donnees de la base de donnee
  cd /var/www/html/wordpress
  wp db export /root/backup/"wordpress-$(date +"%m-%d-%Y")"/BddBackup.$(date +"%m-%d-%Y").sql >> $LOG_LOCATION/result.log 2>&1

# sauvegarde des donnees wordpress
  cd /var/www/html/
  tar -v -cpPzf "/root/backup/"wordpress-$(date +"%m-%d-%Y")"/WordpressBackup.$(date +"%m-%d-%Y").tar.gz" wordpress/

  File=/root/backup/"wordpress-$(date +"%m-%d-%Y")"/WordpressBackup.$(date +"%m-%d-%Y").tar.gz
  test -f $File && echo " the backup is successfully created." >> $LOG_LOCATION/result.log 2>&1
