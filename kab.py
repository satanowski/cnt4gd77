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
Simple webscrapper for getting list of members of SP5KAB club

Copyright (C) 2017-2018 Satanowski <satanowski@gmail.com>
License: GNU AGPLv3
"""

import logging as log
from requests import get

from pyquery import PyQuery as pq


log.basicConfig(level=log.DEBUG)


class KAB:
    """Extract data from SP5KAB website."""

    __URL__ = 'https://sp5kab.pl/czlonkowie/'


    @staticmethod
    def _retrieve(url):
        """Retrieve website of given url."""
        headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537." \
                          "36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safar" \
                          "i/537.36"
        }

        req = get(url, headers=headers)
        if req.status_code != 200:
            log.error('Cannot retrieve data from KAB site!')
            return None

        return req.content.decode()

    @staticmethod
    def retrieve_members():
        """Parse club site to get callsigns of club members."""
        members = []
        parser = pq(KAB._retrieve(KAB.__URL__))

        for member in map(lambda li: li.text.split(), parser('.entry-content li')):
            if len(member) > 1:
                members.append(member[-1])

        return members
