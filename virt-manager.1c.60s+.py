#!/usr/bin/env python3
# encoding: utf-8
"""
Displays and allows you to manage running VMs from the system tray. This only
works if you are running Gnome Shell and install the Argos gnome-shell-extension.
Symlink this script to ~/.config/argos and you should be good to go.
  Argos Extension: https://extensions.gnome.org/extension/1176/argos/
  Argos Documentation: https://github.com/p-e-w/argos
"""
import re, subprocess
from PIL import Image, ImageDraw
from base64 import b64encode
from io import BytesIO
from shlex import split


def _get_machines():
    """ Return a list of all VMs running or not. """
    vms = []
    result = subprocess.check_output(split('virsh list --all'))
    for line in result.decode().split('\n'):
        matches = re.findall(r'\s*([\d-]+)\s+(\w+)\s+(\w+)', line)
        if matches:
            id, name, status = matches[0]
            vms.append({'id':id, 'name':name, 'status':status})
    return sorted(vms, key=lambda vm: (vm['status'], vm['name']))


def _get_ipaddr(name):
    """ Return the ip address of the specified machine name. """
    result = subprocess.check_output(split(f'virsh -c qemu:///system domifaddr {name} --source agent'))
    for line in result.decode().split('\n'):
        if 'eth0' in line:
            name, mac, protocol, ipaddr = line.split()
            if protocol == 'ipv4' and ipaddr != 'N/A':
                return ipaddr.split('/')[0]
    return ''


def circle(color, size=(10,10)):
    """ Create a circle icon image. """
    img = Image.new('RGBA', size, color=color)
    bigsize = (img.size[0]*10, img.size[1]*10)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(img.size, Image.ANTIALIAS)
    img.putalpha(mask)
    buffered = BytesIO()
    img.save(buffered, format='PNG')
    return b64encode(buffered.getvalue()).decode('utf8')


def titleize(count, suffix):
    """ Pluralize the title. """
    suffix += 's' if count != 1 else ''
    return f'{count} {suffix}'


if __name__ == '__main__':
    # Display the Argos output
    vms = _get_machines()
    running = len([vm for vm in vms if vm['status'] == 'running'])
    print(f'{titleize(running, "VM")}\n---')
    for vm in vms:
        color = '#B7B840' if vm['status'] == 'running' else '#918275'
        ipaddr = _get_ipaddr(vm['name'])
        ipaddrstr = f' - {ipaddr}' if ipaddr else ''
        print(f"{vm['name']} {ipaddrstr} | image={circle(color)}")
        if vm['status'] == 'running':
            console = f'virt-manager --connect qemu:///system --show-domain-console {vm["name"]}'
            print(f'--View Browser | href="https://{ipaddr}"')
            print(f'--View Console | terminal=false bash="{console}"')
            print(f'--Shutdown | terminal=false bash="virsh shutdown {vm["name"]}"')
        else:
            print(f'--Start | terminal=false bash="virsh start {vm["name"]}"')
    print('Open Virt Manager | terminal=false bash="virt-manager"')
