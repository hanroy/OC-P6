#! /usr/bin/env python3
#coding: utf-8

"""
============================================
        Automate wordpress backup
            Powered by Python
            Author : Hanen Royer
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
import argparse
import shutil
import logging as lg

try:
    import tqdm
except ImportError:
    print ("Trying to Install required module: tqdm")
    os.system('pip3 install tqdm')
from tqdm import tqdm


try:
    import ftplib
except ImportError:
    print ("Trying to Install required module: ftplib")
    os.system('pip3 install ftplib')
from ftplib import FTP_TLS, error_perm

#######################################################
# Log to both logfile and console                        #
#######################################################

lg.basicConfig(filename="log.txt", filemode='a', format='%(asctime)s : %(levelname)s : %(message)s', datefmt='%d/%m/%Y %H:%M', level=lg.DEBUG)
console = lg.StreamHandler()
console.setLevel(lg.INFO)
formatter = lg.Formatter('%(message)s')
console.setFormatter(formatter)
lg.getLogger('').addHandler(console)


#######################################################
# variables                                           #
#######################################################

today = date.today()
d1 = date.today().strftime("%m-%d-%Y")

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True, type=str)
args = parser.parse_args()

with open(args.input) as json_data:
    try:
        data = json.load(json_data)
    except json.JSONDecodeError:
        print('Invalid JSON format')


wp_backup_path = (data["wp_bkp_local_path"]) +d1   #set wordpress backup folder
days = int((data["days"])) #set days
folder = (data["folder"]) +d1 #set wordpress folder name
backuppath = (data["wp_bkp_path"]) #set wordpress path location
ftp_ip = (data["ftp_ip"]) #set ftp IP
ftp_port = int((data["ftp_port"])) #set ftp port
ftp_login = (data["ftp_login"]) #set ftp login
ftp_password = (data["ftp_password"]) #set ftp password
shell_script = (data["shell_script"])


#######################################################
# Wordpress clean backup folder                       #
# Delete folder older than 5 days                     #
#######################################################

lg.info(f"Delete wordpress backup folder older than {days} days")

def clean_local_wpbackup():

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


clean_local_wpbackup()

#######################################################
# Wordpress create backup folder                      #
#######################################################

lg.info('Create wordpress backup folder with today date')


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

lg.info('Backup wordpress database and compress wordpress path with today date')
def call_shell_backupbdd():
    try:
        file = open(shell_script, 'r')
        lg.info(f'{shell_script} exist!')
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

lg.info('Send wordpress backup folder to FTP server')

try:
    ftps = FTP_TLS(timeout=100)
    ftps.connect(ftp_ip, ftp_port)
    ftps.auth()
    ftps.prot_p()
    ftps.set_pasv(True)
    ftps.login(ftp_login, ftp_password)
    print('Connect to FTP ...')
    print(ftps.getwelcome())


except ftplib.error_perm as e:
    print( 'Ftp fail -> ', e )

ftps.nlst()
files_list = ftps.nlst()
lg.info("List of FTP remote folders:")
for filename in files_list:
    lg.debug(f'{filename} ')


if folder in ftps.nlst() : #check if 'wordpress-todayDate' exist inside '/home/wordpress'
    ftps.cwd(folder) #change into "wordpress-todayDate" directory
    lg.debug(f'{folder} ')
else :
    ftps.mkd(folder) #Create a new directory called "wordpress-todayDate" on the server.
    lg.debug(f'{folder} 2')
    ftps.cwd(folder)

def placeFiles():
    for file in os.listdir(wp_backup_path):
        localpath = os.path.join(wp_backup_path, file)
        if os.path.isfile(localpath):
            filesize = os.path.getsize(localpath)
            #print("STOR", file, localpath)
            with tqdm(unit = 'blocks', unit_scale = True, leave = False, miniters = 1, desc = 'Uploading Files......', total = filesize) as tqdm_instance:
                ftps.storbinary('STOR ' + file, open(localpath,'rb'), 128, callback = lambda sent: tqdm_instance.update(len(sent)))

#print('Send Wordpress backup folder in progress ..')
lg.info('Send Wordpress backup folder in progress ..')
placeFiles()
lg.debug('Wordpress backup folder successfully sent ')
#print('Quit FTP connection')
ftps.quit()
lg.info('Closing FTP connection')
ftps.close() #close connection


