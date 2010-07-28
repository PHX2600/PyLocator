#!/usr/bin/python

import re 
import os 
import sys
import datetime

try:
	import urllib
except:
	print "You are missing the urllib module"
	
try: 
	import MySQLdb
except:
	print "You are missing MySQLdb module"

##MySQL Vars##
server   = ""
user     = ""
password = ""
table    = ""

##Sendmail Vars##
mail="cbock@asu.edu" # Admin email address
sendmail = "/usr/sbin/sendmail" # Sendmail location

##REGEX##
IpAddress = '((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))(?![\\d])'
Location  = '(UNITED STATES'+'.'+'.*?'+'(?:[a-z][a-z]+)'+'.'+'.*?'+'(?:[a-z][a-z]+))'	
LatLong   = '(([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'+'\\s+'+'LATITUDE'+'.'+'(\\s+'+'[+-]?\\d*\\.\\d+)(?![-+0-9\\.])'+'\\s+'+'LONGITUDE)'
ISP       = '(ISP)'+'(:)'+'(\\s+)'+'(<b>)'+'((?:[a-z][a-z]+))'+'(<\\/b>)'


def getPage(url):
	response = urllib.urlopen(url)
	return response.read()

def doRegex(regex, target, group):

	rg = re.compile(regex,re.IGNORECASE|re.DOTALL)
	m = rg.search(target)
	if m:
		return m.group(group)
	else:
		return "NULL"

def Main():
	html=getPage('http://ip2location.com')
	ip=doRegex(IpAddress,html,1)
	location=doRegex(Location,html,1)
	coordinates=doRegex(LatLong,html,1)

	html=getPage('http://tools.ip2location.com/ib1')
	isp=doRegex(ISP,html,5)

	now = datetime.datetime.now()
	time=now.strftime("%y:%m:%d:%H:%M")

	try:
		db = MySQLdb.connect(server,user,password,table)
		cursor = db.cursor()
		cursor.execute ("INSERT INTO Location (id, time, ip, location, coordinates, isp) VALUES"+" (NULL, '"+time+"', '"+ip+"', '"+location+"', '"+coordinates+"', '"+isp+"')")
		db.close()
	except:
		print "Failed To connect to Database"

  		p = os.popen("%s -t" % sendmail, "w")
  		p.write("To: "+mail+"\n")
  		p.write("Subject: DB Connecton failure\n")
  		p.write("\n")
  		p.write(str(os.uname())+"\n"+time+"\n"+ip+"\n"+location+"\n"+coordinates+"\n"+isp+"\n")
  		sts = p.close()
 		if sts != 0:
     			print "Sendmail exit status", sts

	
if __name__ == '__main__':
	
	Main()

