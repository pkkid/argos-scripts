#!/usr/bin/env python3
# encoding: utf-8
"""
Bitbucket Pull Requests
  Argos Extension: https://extensions.gnome.org/extension/1176/argos/
  Argos Documentation: https://github.com/p-e-w/argos
"""
import argparse
import jstyleson
import os
import requests
from PIL import Image
from PIL import ImageDraw
from base64 import b64encode, b64decode
from io import BytesIO
from requests.auth import HTTPBasicAuth

PRS = '{host}/rest/api/latest/inbox/pull-requests?role={role}&start=0' \
    '&limit=10&avatarSize=64&withAttributes=true&state=OPEN&order=oldest'
CACHENAME = '%s-cache.json' % os.path.basename(__file__).split('.')[0]
CACHEFILE = os.path.join(os.path.dirname(__file__), CACHENAME)
cache = {}  # global cache object


def _getkey(lookup):
    """ Fetch the specified key. """
    group, name = lookup.lower().split('.')
    for path in ('~/.config/keys.jsonc', '~/Private/keys/keys.jsonc'):
        filepath = os.path.expanduser(path)
        if not os.path.exists(filepath): continue  # noqa
        with open(filepath, 'r') as handle:
            value = jstyleson.load(handle).get(group, {}).get(name)
            if value is None: continue  # noqa
            if not value.startswith('b64:'): return value  # noqa
            return b64decode(value[4:]).decode('utf8')
    raise Exception(f'Key not specified: {lookup}')


def _get_bitbucket_auth():
    """ Fetch Bitbucket authentication token. """
    host = _getkey('bitbucket.host')
    auth = HTTPBasicAuth(*_getkey('bitbucket.auth').split(':'))
    return host, auth


def _get_image(host, user, size=(25, 25)):
    """ Fetch the image for the specified issuetype. """
    global cache
    if not cache and os.path.isfile(CACHEFILE):
        with open(CACHEFILE, 'r') as handle:
            cache = jstyleson.load(handle)
    if user['name'] not in cache:
        try:
            response = requests.get(f'{host}{user["avatarUrl"]}')
            # Create the 10x10 image
            img = Image.open(BytesIO(response.content))
            img = img.resize(size, Image.ANTIALIAS)
            bigsize = (img.size[0] * 10, img.size[1] * 10)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(img.size, Image.ANTIALIAS)
            img.putalpha(mask)
            buffered = BytesIO()
            img.save(buffered, format='PNG')
            imgstr = b64encode(buffered.getvalue()).decode('utf8')
            cache[user['name']] = imgstr
            with open(CACHEFILE, 'w') as handle:
                jstyleson.dump(cache, handle)
        except Exception:
            return circle('#918275', size)
    return cache.get(user['name'], '')


def _is_reviewed(user, reviewers):
    for reviewer in reviewers:
        if reviewer['status'] == 'NEEDS_WORK' and reviewer['user']['name'] == user:
            return True
    return False


def _getprs(host, auth, role, debug=False):
    """ Get pull requests. role must be one of AUTHOR, REVIEWER. """
    try:
        prs = []
        url = PRS.replace('{host}', host)
        url = url.replace('{role}', role)
        response = requests.get(url, auth=auth)
        response = response.json()
        if response.get('errors'):
            raise Exception(response['errors'][0].get('message', 'Error fetching prs'))
        for pr in response['values']:
            if debug:
                print(jstyleson.dumps(pr, indent=2))
                print('---')
                print(auth.username)
            if _is_reviewed(auth.username, pr['reviewers']):
                continue
            user = pr['author']['user']['displayName'].split()[0]
            title = pr['title'][:80]
            if pr['title'][:6] not in ('[UNTY-', '[NO-JI'):
                title = pr.get('description', '').strip().replace('*', '').replace('\n', '')
                title = ' '.join(title.split())[:80]
            href = pr['links']['self'][0]['href']
            img = _get_image(host, pr['author']['user'])
            fromref = pr['fromRef']['displayId'][:30]
            toref = pr['toRef']['displayId'][:30]
            prs.append((user, title, href, fromref, toref, img))
        return prs
    except Exception as err:
        print(f'Err\n---\n{err}')
        raise SystemExit()


def circle(color, size=(10, 10)):
    """ Create a circle icon image. """
    img = Image.new('RGBA', size, color=color)
    bigsize = (img.size[0] * 10, img.size[1] * 10)
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
    if count == 0:
        return f'{suffix}s'
    suffix += 's' if count != 1 else ''
    return f'{count} {suffix}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bitbucket script for Argos')
    parser.add_argument('--debug', default=False, action='store_true', help='enable debug logging')
    opts = parser.parse_args()
    # Display the Argos output
    host, auth = _get_bitbucket_auth()
    prs = _getprs(host, auth, 'AUTHOR', opts.debug)
    prs += _getprs(host, auth, 'REVIEWER', opts.debug)
    print(f'{titleize(len(prs), "PR")}\n---')
    for user, title, href, fromref, toref, img in prs:
        print(f'{title[:60].strip()}\\n<span color="#999"><small>{fromref} → {toref}</small></span> | href="{href}" image="{img}"')
    if not prs:
        print(f'No pull requests | color=#888')
    print(f'Go to Bitbucket | href="{host}"')
