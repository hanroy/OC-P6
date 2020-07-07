#! /usr/bin/env python3

"""
============================================
        Automate wordpress backup
            Powered by Python
============================================
"""


#######################################################
# import modules                                      #
#######################################################

import os
import sys
import subprocess
from subprocess import Popen, PIPE
from datetime import date
import time
import json
import shutil
import logging as lg
from ftplib import FTP_TLS, error_perm

lg.basicConfig(level=lg.DEBUG)

today = date.today()
d1 = today.strftime("%m-%d-%Y")


#######################################################
# variables                                           #
#######################################################

with open("/root/backup-wp/variables.json", "r") as f:
    my_dict = json.load(f)

wp_backup_path = (my_dict["wp_bkp_local_path"]) +d1   #set wordpress backup folder
days = int((my_dict["days"])) #set days
folder = (my_dict["folder"]) +d1 #set wordpress folder name
backuppath = (my_dict["wp_bkp_path"]) #set wordpress path location
ftp_ip = (my_dict["ftp_ip"]) #set ftp IP
ftp_port = int((my_dict["ftp_port"])) #set ftp port
ftp_login = (my_dict["ftp_login"]) #set ftp login
ftp_password = (my_dict["ftp_password"]) #set ftp password
shell_script = (my_dict["shell_script"])

#######################################################
# Wordpress clean backup folder                       #
# Delete folder older than 5 days                     #
#######################################################


"""
============================================
    	Automate wordpress backup
============================================
"""

def main():

	# initialise the count
	deleted_folders_count = 0

	# convert days in seconds
	# time.time() returns current time in seconds
	seconds = time.time() - (days * 24 * 60 * 60)

	# check if folder exist
	if os.path.exists(backuppath):

		# iterating over each and every folder in the path
		for root_folder, folders, files in os.walk(backuppath):

			# comparing the days
			if seconds >= get_folder_age(root_folder):

				# removing the folder
				remove_folder(root_folder)
				deleted_folders_count += 1 # incrementing count

				break # breaking after removing the root_folder

			else:

				# checking folder from the root_folder
				for folder in folders:

					# folder path
					folder_path = os.path.join(root_folder, folder)

					# comparing with the days
					if seconds >= get_folder_age(folder_path):

						# invoking the remove_folder function
						remove_folder(folder_path)
						deleted_folders_count += 1 # incrementing count


	lg.debug(f"Total folders deleted: {deleted_folders_count}")


def remove_folder(backuppath):

	# removing the folder
	if not shutil.rmtree(backuppath):
		lg.debug(f'{backuppath} is removed successfully') # success message

	else:
		lg.error(f'Unable to delete the {backuppath}') # failure message



def get_folder_age(path):

	ctime = os.stat(path).st_ctime # getting ctime of the folder # time will be in seconds

	return ctime # returning the time


if __name__ == '__main__':
	main()


#######################################################
# Wordpress create backup folder                      #
#######################################################

def create_wp_bkp_folder():
    CHECK_FOLDER = os.path.isdir(wp_backup_path)
    if not CHECK_FOLDER:
        try:
            os.mkdir(wp_backup_path)
            lg.debug(f'{wp_backup_path} Created')
        except OSError:
            if OSError.errno != os.errno.EEXIST:
                raise
    else:
        lg.debug(f'{wp_backup_path} exists! No need to create again')


create_wp_bkp_folder()

#######################################################
# Call backupbdd.sh which :                           #
## backup database data                               #
## backup wordpress folder and compress               #
#######################################################

def call_shell_backupbdd():
    try:
        file = open(shell_script, 'r')
        lg.info(f'{file} exist!')
        session = subprocess.Popen([shell_script], stdout=PIPE, stderr=PIPE)
        lg.info('The backup is successfully executed')
        stdout, stderr = session.communicate(input="Hello from the other side!")
        if stderr:
            raise Exception("Error "+str(stderr))
            lg.critical(stderr)

    except IOError:
        print("file not exist!")
        sys.exit(1)


call_shell_backupbdd()

#######################################################
# Send wordpress backup folder to ftp server          #
#######################################################

try:
    import ftplib
except:
    print()
    print("ftplib , module Not Found")
    print("Install: pip3 install ftplib")
    sys.exit(1)

try:
    ftps = FTP_TLS(timeout=100)
    ftps.connect(ftp_ip, ftp_port)
    ftps.auth()
    ftps.prot_p()
    ftps.set_pasv(True)
    ftps.login(ftp_login, ftp_password)
    print(ftps.getwelcome())


except ftplib.error_perm as e:
    print( 'Ftp fail -> ', e )

ftps.nlst()
files_list = ftps.nlst()
print("List of remote folders:")
for filename in files_list:
    lg.debug(f'{filename} ')


if folder in ftps.nlst() : #check if 'wordpress-todayDate' exist inside '/home/wordpress'
    ftps.cwd(folder) #change into "wordpress-todayDate" directory
else :
    ftps.mkd(folder) #Create a new directory called "wordpress-todayDate" on the server.
    ftps.cwd(folder)

def placeFiles():
    for file in os.listdir(wp_backup_path):
        localpath = os.path.join(wp_backup_path, file)
        if os.path.isfile(localpath):
            print("STOR", file, localpath)
            ftps.storbinary('STOR ' + file, open(localpath,'rb'))

placeFiles()

ftps.quit()
print('Closing FTP connection')
ftps.close() #close connection

