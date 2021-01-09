import socket, threading, sys, os, time, json, logging

try:
    from jnpr.junos import Device
    from jnpr.junos.utils.scp import SCP
    from jnpr.junos.utils.sw import SW
    from jnpr.junos.exception import ConnectError
    

except:
    print("This script uses Junos PyEz, make sure to install the required module")
    sys.exit()
# Tries to import Junos PyEZ, closes the script on failure.

global cwd
cwd = os.getcwd()
# Store current working directory as global variable.

class Junos_ZTP(threading.Thread):
    def __init__(self, ip_address, mac_address):
        # No specific module is called so server calls __init__ Module
        threading.Thread.__init__(self)
        # Passes active thread to class.
        print("Pausing to allow address to bind")
        time.sleep(10)
        # Sleeping 10 seconds to allow the SRX to fully bind the DHCP address.
        print("Launching OOB Firmware module")
        self.OOB_Firmware(ip_address, mac_address)
        # Launches firmware module and passes IP and MAC.
        

    def OOB_Firmware(self, ip_address, mac_address):
        mac_format = mac_address.replace(":", "")
        # Format the MAC without colons, this is used for the file name to create a unique filename per log file.
        package = "junos-srxsme-20.1R2.7.tgz"
        # Junos OS can be specified here.
        host = ip_address
        user = 'root'
        passwd = 'Pl4ceholder'
        # Pulls IP address from DHCP as host IP. Uses temp credentials that are wiped when Config file is applied.
        logfile = cwd + "/%s_log.txt" % (mac_format)
        # Creates variable for log file location.
        print(logfile)
        self.CreateLogFile(logfile)
        # Runs the create log file module.

        self.LogInitialise(host, logfile)
        # Runs the log Initialise module.
        dev = Device(host=host, user=user, passwd=passwd)
        try:
            dev.open()
        # Uses pyEZ module to open a session to the device
        except ConnectError as err:
            logging.error ("Cannot connect to device {0}\n".format(err))
            return
        # If it can't open session close the thread.

        sw = SW(dev)
        # Opens the PyEZ software module on current active session.

        try:
            logging.info("Starting Software upgrade {0}".format(package))     
            ok, msg  = sw.install(package=package, validate=False, progress=self.progressreport)   
            # starts to install firmware package. Uses progressreport module to keep track of progress
            # Package is specified here, by default it will look in the current working directory for the OS package but can be specified otherwise.
            # By default it copies the firmware to the /var/tmp/* directory.
            # It will then install the firmware after copy (which can take a while...) No logs are displayed during the install

        except Exception as err:
            msg = 'Unable to install software, {0}'.format(err)
            print("Unable to install software")
            logging.error(msg)
            ok = False
            # Will state if it's unable to copy/find the firmware and sets ok to false. (also if the firmware install fails too)

        if ok is True:
            logging.info('Software installation complete. Rebooting.')
            print("Rebooting")
            rsp = sw.reboot()
            logging.info('Upgrade pending reboot cycle')
            logging.info(rsp)
            # If copy is successful "ok" will be True and trigger a reboot to complete firmware update.
        else:
            print('Unable to install software')
            logging.error(msg)
            # If false then it will close the thread without reboot.

        dev.close()
        print("Terminating thread")
        # Close active device session.

    def CreateLogFile(self, logfile):

        if os.path.isfile(logfile):
            print("File Exists")
            # Checks to see if log file already exists
        else:
            open(logfile, 'a').close()
            # If not then log file is created (logging module is not capable of creating new log files.)



    def LogInitialise(self, host, logfile):

        logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s:%(name)s: %(message)s')
        logging.getLogger().name = host
        logging.getLogger().addHandler(logging.StreamHandler())
        logging.info('Information logged in {0}'.format(logfile))
        # Initialises the log file, specifies formats.


    def progressreport(self, dev, report):
        print("host: %s, report: %s" % (dev.hostname, report))
        # Juniper capable of show progress reports in print (not logging but may need more testing).
        # This shows the progress as it copies the firmware to the SRX.



def main():
    
    CONNECTION_LIST = []
    RBUFFER = 4096
    PORT = 5000
    HOST = "0.0.0.0"
    ServerIP = socket.gethostbyname(socket.gethostname())
    # Create empty Connection list array to keep track of active connections
    # Buffer size, port, and blank host variables and store the Server IP as a variable using socket get host modules.

    ServSession = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ServSession.bind((HOST, PORT))
    ServSession.setblocking(10)
    ServSession.listen(20)
    # Create socket using AF_INET address family and stream socket type and bing host and port to session 
    # Setblocking lists timeout to complete TCP request and listen flag to state maximum number of active sessions.

    CONNECTION_LIST.append(ServSession)
    print("Server started on port " + str(PORT))
    print("Server IP is " + ServerIP)
    print("Server currently listening for clients...")
    # Adds new sission to array

    while True:
        connect, address = ServSession.accept()
        print(str(address) + "has been detected as a new lease.")
        # Server now constantly loops listening for connections, when it receives a connection request from the client.
        lease_msg = connect.recv(RBUFFER).decode()
        lease_msg_construct = json.loads(lease_msg)
        # Server will recieve the message from client (dictionary string containing OS, IP and MAC) and convert it back into a dictionary.

        if lease_msg_construct["ztp"] == "junos":
            # Dictionary should contain the firmware sent from the client. This is to futureproof (for example add an elif for cisco or aruba if needed).
            print("Detected Junos ZTP request, starting thread")
            t = Junos_ZTP(lease_msg_construct["ip_address"], lease_msg_construct["mac_address"])
            t.start()
            # If it contains the junos flag it starts the Junos_ZTP class and passes the IP and Mac address from the dictionary.
            # Closes socket connection at this point as connection is established between SRX and server.
        
        else: 
            print("Unknown connection.")
            print(lease_msg_construct)
            # If the ztp ID doesn't containt junos, then the the connection is unknown the the connection is closed.

        continue



if __name__ == '__main__':
    main()
#Usual If main statement, runs the program and doesn't allow it to be imported to other scripts.