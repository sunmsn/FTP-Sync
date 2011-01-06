This script was created by Devin Cornell
http://devincornell.me
dz3.public@gmail.com

This python program basically runs a loop that will scan 
through your files in a desired directory, and attempt 
to mirror your files and structure as they appear on the 
local machine. It uses FTP from ftplib, os, Thread from 
threading, and time modules to do this. It will create a 
database called files.db to store a record of your files. 
If you would not like to re-upload all of your files each 
time you restart the program, don't delete this file in 
between runnings. Just edit the variables at the top of 
the script to customize it for your server, etc.

I made it rather quickly, so it's probably still pretty 
buggy. It's good enough for my purposes, but don't blame 
me if it messes up your data on the server or something. 
If you have any questions, please feel free to email me 
at dz3.public@gmail.com.
