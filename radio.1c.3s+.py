#!/usr/bin/env python3
# encoding: utf-8
"""
Internet Radio using VLC
  Argos Extension: https://extensions.gnome.org/extension/1176/argos/
  Argos Documentation: https://github.com/p-e-w/argos
"""
import os, subprocess
from shlex import split

STATIONSNAME = '%s-stations.txt' % os.path.basename(__file__).split('.')[0]
STATIONSFILE = os.path.join(os.path.dirname(__file__), STATIONSNAME)
DEFAULT_STATIONS = [
    ('90.5 WBER Alternative', 'http://wber.org/wber.m3u'),
    ('Idobi Alternative', 'http://69.46.75.98/'),
    ('Lounge Radio', 'http://77.235.42.90/;stream/1'),
]


def _get_stations():
    """ Return the full list of radio stations. """
    stations = []
    # Read the configuration file
    if os.path.isfile(STATIONSFILE):
        with open(STATIONSFILE, 'r') as handle:
            for line in handle.read().strip().split('\n'):
                stations.append(line.rsplit(' ', 1))
        return stations
    # Write the configuration file
    with open(STATIONSFILE, 'w') as handle:
        for name, href in DEFAULT_STATIONS:
            handle.write(f'{name} {href}\n')
    return DEFAULT_STATIONS


def _current_station():
    """ Return the current radio station. """
    comment = '# station:'
    result = subprocess.check_output(split('ps ax'))
    for line in result.decode().split('\n'):
        if comment in line:
            return line.split(comment)[-1].strip()
    return 'Radio'
    

if __name__ == '__main__':
    current = _current_station()
    print(f'{current[:9]}\n---')
    for name, url in _get_stations():
        print(f"{name} | terminal=false bash=\"killall vlc; vlc -I dummy {url} # station:{name}\"")
    print('---\nStop Playback | terminal=false bash="killall vlc"')
