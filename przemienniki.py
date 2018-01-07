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
Simple wrapper for przemienniki.net API

Copyright (C) 2017-2018 Satanowski <satanowski@gmail.com>
License: GNU AGPLv3
"""


import logging as log

from collections import namedtuple

from lxml import etree
from requests import get


log.basicConfig(level=log.DEBUG)


class PrzemiennikiWrapper:
    """Simple wrapper for https://przemienniki.net API."""

    API_URL = 'https://przemienniki.net/export/rxf.xml?country=pl&onlyworking'
    REP = namedtuple('Repeater', 'sign,modes,working,bands,freqs,activation,'\
                                 'tones')

    def __init__(self):
        self.repeaters = []
        self.bands = set()
        self.modes = set()
        self.get_repeaters()

    @staticmethod
    def _ext_many(obj, field):
        return list(map(lambda r: r.text, obj.findall(field)))

    @staticmethod
    def _ext_many_attr(obj, field, attr):
        return list(
            map(lambda r: {r.attrib[attr]: r.text}, obj.findall(field))
        )

    @staticmethod
    def _merge_dicts(dicts):
        if len(dicts) == 2:
            a, b = dicts
            return {**a, **b}
        else:
            return dicts

    @staticmethod
    def _extract_repeater_data(obj):

        tones = PrzemiennikiWrapper._ext_many_attr(obj, 'ctcss', 'type')
        if len(tones) > 1:
            tones = PrzemiennikiWrapper._merge_dicts(tones)
        elif len(tones) == 1:
            tones = tones[0]
        else:
            tones = {}

        return PrzemiennikiWrapper.REP(
            sign=obj.find('qra').text,
            modes=PrzemiennikiWrapper._ext_many(obj, 'mode'),
            working=obj.find('statusInt').text == '1',
            bands=PrzemiennikiWrapper._ext_many(obj, 'band'),
            freqs=PrzemiennikiWrapper._ext_many_attr(obj, 'qrg', 'type'),
            activation=PrzemiennikiWrapper._ext_many(obj, 'activation'),
            tones=tones
        )

    def get_repeaters(self):
        """Get and parse XML from API, extract Repeater's data."""
        parser = etree.XMLParser(recover=True)
        try:
            root = etree.fromstring(
                get(self.API_URL).content,
                parser=parser
            )
        except:
            log.error('Cannot retrieve or parse XML!')
            return 0

        self.repeaters.clear()
        for repeater in root.iter('repeater'):
            data = self._extract_repeater_data(repeater)
            self.bands.update(set(map(str.lower, data.bands)))
            self.modes.update(set(data.modes))
            self.repeaters.append(data)

        self.bands = sorted(list(self.bands))
        self.modes = sorted(list(self.modes))
        return len(self.repeaters)
