####Updating JunOS Firmware via DHCP using Python Automation (Zero Touch Provisioning)####

This repository contains the code for the following blog post:

#####Summary#####

The code is for updating the firmware of a JunosOS device (specifically the SRX300) with any desired firmware present in the same repository.

The code requires a DHCP server configured to run the client script on DHCP lease. A separate network device running the ZTP server script.

More details and a full write up of the script are available via the blog post above including the requirements, caveats to this script and possible improvements that need to be made.