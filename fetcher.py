#
# Copyright 2017-2018 by Satanowski
#

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.

# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.


"""

Copyright (C) 2017-2018 Satanowski <satanowski@gmail.com>
License: GNU AGPLv3
"""

import threading

import logging as log
from requests import get


log.basicConfig(level=log.DEBUG)


EXT_SOURCES = {
    'rep': 'https://przemienniki.net/export/rxf.xml',
    'dmr': 'http://dmr.ham-digital.net/user_by_call.php',
    'kab': 'https://sp5kab.pl/czlonkowie/',
}

HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,"\
                  " like Gecko) Chrome/63.0.3239.84 Safari/537.36",
}

LOCK = threading.Lock()


def fetch(key: str, url: str, output: dict):
    """Fetch content of the page og iven url and put it into 'output' dict."""
    resp = get(url, headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        log.error("Fetch error (%s): %s", url, resp.status_code)
        with LOCK:
            output[key] = None
        return
    with LOCK:
        output[key] = resp.content.decode('utf-8')
        log.debug('Got %d bytes for %s', len(resp.content), key)


def fetch_urls() -> list:
    """Fetch all configured URL and strore received content."""
    results = {}

    for source in EXT_SOURCES:
        threading.Thread(
            target=fetch,
            args=(source, EXT_SOURCES[source], results)
        ).start()

    for thread in threading.enumerate():
        if thread != threading.current_thread():
            thread.join()

    return results
x