import socket, time, sys, json

def main():

    host = "172.16.20.200" 
    # Set host as server
    port = 5000
    # Set port for communication at 5000
    Local_IP = sys.argv[1]
    Local_MAC = sys.argv[2]
    # Sets local IP and MAC sent from DHCP via system arguments
    msg = {"ztp": "junos", "ip_address": Local_IP, "mac_address": Local_MAC}
    # Create a dictionary containing the information to sent to ZTP server
    msg_format = json.dumps(msg)
    # Use JSON String Dump to send the information as a string (sending a dictionary is not supported)
    CliSession = socket.socket()
    CliSession.connect((host, port))
    CliSession.send(msg_format.encode())
    CliSession.close()
    # Opens socket session using server IP and port, sends the json string (encoded in bytes) and closes session.



if __name__ == '__main__':
    main()