'''this module has one purpose... provide a connection to the mysqldatabase
using 3rd party MySQLdb module'''

import MySQLdb
import sys
import base64
from xml.dom import minidom
from openmolar.settings import localsettings 

mainconnection, forumconnection = None, None

print "parsing the global settings file"
dom = minidom.parse(localsettings.cflocation)

settingsversion = dom.getElementsByTagName("version")[0].firstChild.data
    
sysPassword = dom.getElementsByTagName("system_password")[0].firstChild.data
xmlnode = dom.getElementsByTagName("server")[0]
myHost = xmlnode.getElementsByTagName("location")[0].firstChild.data
myPort = int(xmlnode.getElementsByTagName("port")[0].firstChild.data)
sslnode = xmlnode.getElementsByTagName("ssl")

xmlnode = dom.getElementsByTagName("database")[0]
myUser = xmlnode.getElementsByTagName("user")[0].firstChild.data
myPassword = xmlnode.getElementsByTagName("password")[0].firstChild.data
if settingsversion == "1.1":
    myPassword = base64.b64decode(myPassword)

myDb = xmlnode.getElementsByTagName("dbname")[0].firstChild.data

if sslnode and sslnode[0].firstChild.data=="True":
    #-- to enable ssl... add <ssl>True</ssl> to the conf file
    print "using ssl"
    #-- note, dictionary could have up to 5 params.
    #--ca, cert, key, capath and cipher
    #-- however, IIUC, just using ca will encrypt the data
    ssl_settings = {'ca': '/etc/mysql/ca-cert.pem'}
else:
    print "not using ssl (you really should!)"
    ssl_settings = {}

dom.unlink()


class omSQLresult():
    '''
    a class used in returning the result of sql queries
    '''
    def __init__(self):
        self.message = ""
        self.number = 0
        self.result = False
    def __nonzero__(self):
        '''
        used in case the class is used thus
        if omSQLresult:
        '''
        return self.result
    def setMessage(self, arg):
        '''
        set the message associated with the result
        '''
        self.message = arg
    def getMessage(self):
        '''
        get the message associated with the result
        '''
        return self.message
    def setNumber(self, arg):
        '''
        set the number of rows grabbed by the result
        '''
        self.number = arg
    def getNumber(self):
        '''
        get the number of rows grabbed by the result
        '''
        return self.number

def forumConnect():
    '''
    this returns a connection for use by the forum thread
    '''
    global forumconnection
    try:
        if not (forumconnection and forumconnection.open):
            print "New connection needed"
            print "connecting to %s on %s port %s"% (myDb, myHost, myPort)
            forumconnection = MySQLdb.connect(host = myHost, port = myPort,
            user = myUser, passwd = myPassword, db = myDb, ssl = ssl_settings)
            forumconnection.autocommit(True)
        else:
            forumconnection.commit()
        return forumconnection
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        raise localsettings.omDBerror(e)
    
def connect():
    '''
    returns a MySQLdb object, connected to the database specified in the
    settings file
    '''
    global mainconnection
    try:
        if not (mainconnection and mainconnection.open):
            print "New connection needed"
            print "connecting to %s on %s port %s"% (myDb, myHost, myPort)
            mainconnection = MySQLdb.connect(host = myHost, port = myPort,
            user = myUser, passwd = myPassword, db = myDb, ssl = ssl_settings)
            mainconnection.autocommit(True)
        else:
            mainconnection.commit()

        return mainconnection
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        raise localsettings.omDBerror(e)
    

if __name__ == "__main__":
    from openmolar.settings import localsettings
    localsettings.initiate()
    import time
    print localsettings.cflocation
    for i in range(1, 11):
        try:
            print "connecting....",
            dbc = connect()
            print dbc.info()
            print 'ok... we can make Mysql connections!!'
            print "loop no ", i
            if i == 2:
                #close the db... let's check it reconnects
                dbc.close()
            if i == 4:
                #make a slightly bad query... let's check we get a warning
                c = dbc.cursor()
                c.execute('update patients set dob="196912091" where serialno=4')
                c.close()
        except Exception,e:
            print "error", Exception, e
        
        time.sleep(5)

    dbc.close()