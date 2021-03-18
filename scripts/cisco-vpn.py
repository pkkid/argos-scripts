#!/usr/bin/env python3
# encoding: utf-8
# Connect or Disconnect from Cisco Anyconnect VPN Service
# https://computingforgeeks.com/connect-to-vpn-server-with-cisco-anyconnect-from-linux-terminal/
import subprocess
from getkeys import getkey

VPN = '/opt/cisco/anyconnect/bin/vpn'
CREDS = getkey('cisco.vpncreds', prompt=False)
HOST = getkey('cisco.vpnhost', prompt=False)


def vpn_connected():
    output = subprocess.check_output([VPN, 'status']).decode()
    if 'state: Connected' in output:
        return True
    return False


if __name__ == '__main__':
    connected = vpn_connected()
    if connected:
        print('Connected\n---')
        print(f'Disconnect | bash="{VPN} -s disconnect {HOST}"')
    else:
        print('Disconnected\n---')
        print(f'Connect | bash="{VPN} -s  < {CREDS} connect {HOST}"')
