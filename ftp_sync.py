#!/usr/bin/python

#set user vars
database = "files.db" #location on local machine to store database file
root_directory = "" #directory on local machine to upload and scan for changes
ftp_address = "" #ftp address
ftp_directory = "sync/" #directory on remote ftp location to store all of the data uploaded
ftp_username = "" #ftp username
ftp_password = "" #ftp password
n = 3 #number of seconds before checking that the data has not changed - user can set at runtime.

if root_directory[-1:] == "/":
	root_directory = root_directory[:-1]


#import mods
import os
import sqlite3
import time
from ftplib import FTP
from threading import Thread



#def functions


def scan_local_folder (path, ftp, connection, sql):
	#scan filesystem to check for database inconsistencies
	for (root, dirs, files) in os.walk(path):
		for file in files:
			#prepare strings for checking and inclusion
			full_path = root + "/" + file
			rel_path = (root + "/" + file).replace(root_directory, "")
			if rel_path[:1] == "/":
				rel_path = rel_path[1:]
			sql.execute('SELECT * FROM files WHERE full_path = "' + full_path + '"')
			if len(sql.fetchall()) == 0:
				#file does not exist in database
				sql.execute('INSERT INTO files (full_path, rel_path, modified, size) values ("' + full_path + '", "' + rel_path + '", "' + str(os.path.getmtime(full_path)) + '", ' + str(os.path.getsize(full_path)) + ')')
				connection.commit()
				print "File has been modified. Uploading:", rel_path
				upload_file(ftp, root + "/" + file, rel_path)
			sql.execute('SELECT id FROM files WHERE full_path = "' + full_path + '" AND NOT (modified = "' + str(os.path.getmtime(full_path)) + '" OR size = "' + str(os.path.getsize(full_path)) + '")')
			rows = sql.fetchall()
			if len(rows) == 1:
				print "Change detected in", rel_path, "."
				#if file exists in database, but has a different size or mod_date
				sql.execute('UPDATE files SET modified = "' + str(os.path.getmtime(full_path)) + '", size = "' + str(os.path.getsize(full_path)) + '" WHERE id = "' + str(rows[0][0]) + '"')
				print rel_path, "was updated in database. Now uploading to server....."
				upload_file(ftp, root + "/" + file, rel_path)
				print rel_path, "was uploaded."
			#else:
				#print "has not changed:", full_path
	#scan database to check for missing files in filesystem
	sql.execute('SELECT * FROM files')
	database_listings = sql.fetchall()
	for row in database_listings:
		if not os.path.exists(row[1]) or not str(os.path.getmtime(row[1])) == str(row[3]) or not float(os.path.getsize(row[1])) == float(row[4]):
			ftp.cwd("/" + ftp_directory)
			print "Deleting", row[2], "from server. It has been deleted on local machine."
			try:
				ftp.delete(row[2])
			except:
				print "The remote file does not exist on remote server."
			sql.execute('DELETE FROM files WHERE id = "' + str(row[0]) + '"')
			print "Remote file", row[1], "was deleted on server.\n"

def upload_file(ftp, source, dest):
	global ftp_directory
	ftp.cwd("/")

	for folder in ftp_directory.split("/"):
		try:
			ftp.cwd(folder)
		except:
			ftp.mkd(folder)
			ftp.cwd(folder)
			
	for folder in os.path.dirname(dest).split("/"):
		try:
			ftp.cwd(folder)
		except:
			ftp.mkd(folder)
			ftp.cwd(folder)
	
	file_obj = open(source)
	ftp.storbinary('STOR ' + os.path.basename(source), file_obj)

def scan_ftp(ftp_object):
	folders = []
	ftp_object.dir(folders.append)
	for files in folders:
		if files[:1] != "d":
			print files[56:]
		else:
			ftp_object.cwd(files[56:])
			print ftp_object.pwd()

def make_table(sql):
	sql.execute('''CREATE TABLE IF NOT EXISTS files (
		id INTEGER PRIMARY KEY,
		full_path VARCHAR(2000),
		rel_path VARCHAR(2000),
		modified VARCHAR(30),
		size INTEGER(10)
	)''')

def sql_connect():
	connection = sqlite3.connect(database)
	sql = connection.cursor()
	make_table(sql)
	print "Database connection was a success."
	return (connection, sql)

def ftp_connect():
	ftp = FTP(ftp_address)
	ftp.login(ftp_username, ftp_password)
	print "FTP connection was a success."
	return ftp

def timer_loop(n):
	global go
	ftp = ftp_connect()
	connection, sql = sql_connect()
	while go:
		scan_local_folder(root_directory, ftp, connection, sql)
		time.sleep(n)

#start linear model for program
go = True
#timer_loop(n)
while True:
	print "type 'help' if you need help\nlag is set to", n
	input = raw_input(">>")
	if input == "help":
		print "start = will start scaning your filesystem to detect changes\nstop = will stop scanning your filesystem to detect changes\nlag n = will scan filesystem every n seconds\nexit = will call exit()"
	elif input == "start":
		print "Starting ftp sync application"
		scan_service = Thread(target=timer_loop, args=(n,))
		scan_service.start()
		#scan_service.run()
		print "The scan service has started."
	elif input == "status":
		try:
			scan_service.run()
		except:
			print "The scan service has not started yet. Use the 'start' command."
	elif input == "stop":
		go = False
		scan_service.join()
		print "The scan service has stopped."
	elif input[:4] == "lag ":
		n = int(input[4:])
	elif input == "":
		print ""
	elif input == "exit":
		exit()
	else:
		print "Command not recognized."
