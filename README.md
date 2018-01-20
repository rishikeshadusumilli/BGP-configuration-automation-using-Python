# BGP-Config-automation-using-Python

Enable SSHv2 in devices before operating using this script.

1. loggingSSH.py - Script to parse configuration from text file and uploads on to the device
2. bgp.conf - Essential information required to configure BGP
3. sshInfo.conf -  Login credentials and the IPs used to SSH into the two routers
4. runOutputScript.py - Script to retrieve the complete running-config from the routers and upload them to a S3 bucket on AWS
