#!/usr/bin/env python3
"""
Internet Radio using VLC

References:
  Argos Extension: https://extensions.gnome.org/extension/1176/argos/
  Argos Documentation: https://github.com/p-e-w/argos
  Icon Generator: https://www.iconsdb.com/custom-color/circle-icon.html#custom_size
  Base64 Generator: https://www.base64-image.de/
"""
import subprocess
from shlex import split

STATIONS = [
    ('90.5 WBER - Alternative', 'http://wber.org/wber.m3u'),
    ('Idobi Alternative', 'http://69.46.75.98/'),
    ('Lounge Radio', 'http://77.235.42.90/;stream/1'),
    ('Thailand Library', 'http://112.121.150.133:9114/'),
]


def _current_station():
    try:
        result = subprocess.check_output(split('ps ax'))
        for line in result.decode().split('\n'):
            if 'vlc -I dummy' in line:
                station = line.rsplit(' ',1)[-1]
                for name, url in STATIONS:
                    if url == station:
                        return name
    except Exception:
        pass
    return 'Radio'
    

if __name__ == '__main__':
    current = _current_station()
    print(current[:9])
    print('---')
    for name, url in STATIONS:
        print(f"{name} | terminal=false bash=\"killall vlc; vlc -I dummy {url}\"")
    print('---')
    print('Stop Playback | terminal=false bash="killall vlc"')
