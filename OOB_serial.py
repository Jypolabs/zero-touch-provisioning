import sys
import getpass
import re
from time import sleep
try:
    import serial

except:
    print("The script requires the installation of PySerial")
    sleep(7)
    sys.exit()
    
class Junos_OOB_Launch():

    def __init__(self):

        Read_Timeout = 8

        while True:
            try:
                com_port = input("Specify your com port: ")
                console = serial.Serial(
                    port=com_port,
                    baudrate=9600,
                    parity='N',
                    stopbits=1,
                    bytesize=8,
                    timeout=Read_Timeout
                )
                break
            except:
                pass
            print("Unable to open serial connection, check com port used is correct and not currently active then try again.")

        if not console.isOpen():
            print("Console open but has no input, check console connection and try again.")
            sleep(5)
            sys.exit()
                
        default_pass = "Pl4ceholder\r"
        print("Intialising serial conneciton")

        console.write("\r\n\r\n".encode())
        sleep(1)
        output = console.read(console.inWaiting()).decode()
        serial_check_login = re.search('(login:)', output)
        serial_check_shell = re.search('(root@%)', output)
        serial_check_cli = re.search('(root>)', output)
        serial_check_config = re.search('(root#)', output)

        if serial_check_login:
            console.write("root\r".encode())
            sleep(7)
            console.write("cli\r".encode())
            sleep(10)
            output = console.read(console.inWaiting()).decode()

        else:
            
            if serial_check_shell:
                console.write("cli\r".encode())
                sleep(10)
                output = console.read(console.inWaiting()).decode()

            else:

                if serial_check_cli:
                    console.write("\r".encode())
                    sleep(2)
                    output = console.read(console.inWaiting()).decode()
                
                else: 

                    if serial_check_config:
                        print("Junos Device already in configure mode, ensure you log out of the device and attempt to run the script again.")
                        sys.exit()
                    else:
                        print("Unable to reach login prompt, please check connection and confirm the correct com port was specified.")
                        sys.exit()
        print("Serial connection established.")
        console.write("configure\r".encode())
        sleep(2)
        print("Config mode accessed.")
        console.write("set security zones security-zone untrust interfaces ge-0/0/0.0 host-inbound-traffic system-services ssh\r".encode())
        print("Applied SSH as trusted service")
        sleep(2)
        console.write("set security zones security-zone untrust interfaces ge-0/0/0.0 host-inbound-traffic system-services netconf\r".encode())
        print("Applied netconf as trusted service")
        sleep(2)
        console.write("set system root-authentication plain-text-password\r".encode())
        sleep(2)
        console.write(default_pass.encode())
        sleep(2)
        console.write(default_pass.encode())
        sleep(2)
        print("Applied TNP default password.")
        console.write('set system services ssh root-login allow\r'.encode())
        print("Allow root ssh login.")
        sleep(2)
        console.write('commit comment "password and ssh via OOB_serial.py"\r'.encode())
        print("Committing configuration.")
        sleep(20)
        output = console.read(console.inWaiting()).decode()
        print(output)

        console.write("exit\n\r".encode())
        sleep(2)
        console.write("exit\n\r".encode())
        sleep(2)
        console.write("exit\n\r".encode())
        print ("Config applied closing script.")
        sleep(5)

def main():
    Junos_OOB_Launch()

if __name__ == '__main__':
    main()

