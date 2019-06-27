#!/usr/bin/env python3
"""
Displays and allows you to manage running VMs from the system tray. This only
works if you are running Gnome Shell and install the Argos gnome-shell-extension.
Symlink this script to ~/.config/argos and you should be good to go.

References:
  Argos Extension: https://extensions.gnome.org/extension/1176/argos/
  Argos Documentation: https://github.com/p-e-w/argos
  Icon Generator: https://www.iconsdb.com/custom-color/circle-icon.html#custom_size
  Base64 Generator: https://www.base64-image.de/
"""
import re, subprocess
from shlex import split

GREEN = 'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAqklEQVQYlXXPv0oDYRAE8N8cPlJInUouv'\
    'k0IaCNY2KW5VxERc1ilszl8pU3xmfP8N7B8u/vNDjOB13FD6cU+rDVMVYbwst2e5DhuVLlPPCrEd5SDuLvCNY1U7WNG2ngb3rsqu6VA/hItuy6xmhk'\
    '/mV/vqvtFurSLXdAVUz59ZeFvPmjep04ZLiGq+ZlrEXDoEm94+C9MOOApcBw3il7Zi3WaykcxiOeb/uQMuGw9O6IxxsUAAAAASUVORK5CYII='
GREY = 'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAnElEQVQYlX3QMUpDARCE4W8eOVLIESSnUUK'\
    'CNgaLdCHw0JOIWHkBm+CVJkVeIZpkYdhi/hmWDbztNrAsa+0CJMcw4vN+e5AJesbO5dnjaYa7ttcgeEzyPdOukmgryWW0XQ2S+RVTe96S+aztL69/a'\
    'Z1CQ+KYxE1xHMjY1k0xDvhK8nJ+3f827MN74HW3EZZt10kW070/GCUfD9uDE5f3VCMES6L5AAAAAElFTkSuQmCC'


def _get_vms():
    vms = []
    result = subprocess.check_output(split('virsh list --all'))
    for line in result.decode().split('\n'):
        matches = re.findall(r'\s*([\d-]+)\s+(\w+)\s+(\w+)', line)
        if matches:
            id, name, status = matches[0]
            vms.append({'id':id, 'name':name, 'status':status})
    return sorted(vms, key=lambda vm: (vm['status'], vm['name']))


def _get_ipaddr(name):
    try:
        result = subprocess.check_output(split(f'virsh -c qemu:///system domifaddr {name} --source agent'))
        for line in result.decode().split('\n'):
            if 'eth0' in line:
                name, mac, protocol, ipaddr = line.split()
                if protocol == 'ipv4' and ipaddr != 'N/A':
                    return ipaddr.split('/')[0]
        return ''
    except Exception:
        return ''


if __name__ == '__main__':
    vms = _get_vms()
    running = len([vm for vm in vms if vm['status'] == 'running'])
    print(f'{running} VMs' if running else 'VMs')
    print('---')
    for vm in vms:
        icon = GREEN if vm['status'] == 'running' else GREY
        ipaddr = _get_ipaddr(vm['name'])
        ipaddrstr = f' - {ipaddr}' if ipaddr else ''
        print(f'{vm["name"]} {ipaddrstr} | image={icon}')
        if vm['status'] == 'running':
            print(f'--View Browser | href="https://{ipaddr}"')
            print(f'--View Console | terminal=false bash="virt-manager --connect qemu:///system --show-domain-console {vm["name"]}"')
            print(f'--Shutdown | terminal=false bash="virsh shutdown {vm["name"]}"')
        else:
            print(f'--Start | terminal=false bash="virsh start {vm["name"]}"')
    print('Open Virt Manager | terminal=false bash="virt-manager"')
