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
DB updater

Copyright (C) 2017-2018 Satanowski <satanowski@gmail.com>
License: GNU AGPLv3
"""

import sys
import logging as log
from time import time

from lxml import etree
from pyquery import PyQuery as pq

import secret
from fetcher import fetch_urls
from utils import current_date_as_string, fix_country
from db import DB


log.basicConfig(level=log.DEBUG)

class DbUpdater():
    """Iniatilze DB with static data."""

    def __init__(self, credentials):
        start = time()
        self.db = DB(credentials)
        log.info("DB update started...")
        self.DATA = fetch_urls()
        log.info("Raw data fetcher, processing...")
        self.countries = self.db.get_countries_dict()
        log.info("loading dmr contacts...")
        self.load_dmr_contacts()
        log.info("loading repeaters...")
        self.load_repeaters()
        log.info("loading KAB members...")
        self.load_sp5kab_members()
        self.db.store('db_updated', current_date_as_string())
        h, m, s = self.timer(start)
        log.info(
            f"DB updated finished. It took: {h} hours, {m} minutes, {s} s."
        )

    @staticmethod
    def timer(start):
        """Count the time."""
        delta = int(time() - start)
        h = delta//3600
        delta -= h * 3600
        m = delta//60
        s = delta - m * 60
        return h, m, s

    def load_dmr_contacts(self):
        """Load DMR contacts from the web."""
        for i, line in enumerate(self.DATA['dmr'].split("\n")[1:]):
            items = list(map(str.strip, filter(None, line.split(";"))))
            if len(items) < 5:
                continue  # wrong record, skip
            dmr_id = int(items[2])
            country_name = fix_country(items[4])
            if country_name not in self.countries:
                log.warning('New country: %s!', country_name)
                country_name = None

            country_short = self.countries[country_name or '--']

            self.db.add_dmr(
                dmr_id=dmr_id,
                name=items[3],
                call=items[1],
                is_talk_group=False,
                country_short=country_short,
                description=''
            )

            if i % 100 == 0:  # print progress once a while
                sys.stdout.write('\rDMR records loaded: '+ str(i))
        print()

    @staticmethod
    def _extract_ctcss_tones(repeater: object) -> dict:
        """Extract CTCSS info from the XML record."""
        tones = {'rx': None, 'tx': None}
        if repeater.find('activation').text.upper() == 'CTCSS':
            for tone in repeater.findall('ctcss'):
                tones[tone.get('type')] = float(tone.text)
        return tones

    @staticmethod
    def _extract_freqs(repeater: object) -> list:
        """Extract RX/TX freqs from the XML record."""
        freqs = []
        for freq in repeater.findall('qrg'):
            freqs.append((freq.get('type'), float(freq.text)))
        return freqs

    def _get_rep_modes(self, repeater: object) -> list:
        result = []
        for mode in repeater.findall('mode'):
            m = self.db.get_mode_by_ident(mode.text.lower())
            if m and m.supported:
                result.append(m)
            else:
                log.debug('MODE NOT IN DB: %s', mode.text)
                continue

        return result

    def _get_rep_bands(self, repeater: object) -> list:
        result = []
        for _, freq in self._extract_freqs(repeater):
            band = self.db.gues_band(freq)
            if band and band.supported:
                result.append(band)
            else:
                log.debug('Band not in DB: %s', freq)
                continue

        return result

    def load_repeaters(self):
        """Load repeaters data from the web."""
        parser = etree.XMLParser(recover=True)  # pylint: disable=c-extension-no-member
        try:
            root = etree.fromstring(self.DATA['rep'].encode(), parser=parser)  # pylint: disable=c-extension-no-member
        except:  # pylint: disable=bare-except
            return

        for i, repeater in enumerate(root.iter('repeater')):
            modes = self._get_rep_modes(repeater)
            bands = self._get_rep_bands(repeater)
            if not all([modes, bands]):
                continue  # skip - not supported repeater

            call = repeater.find('qra').text
            tones = self._extract_ctcss_tones(repeater)
            freqs = {}

            for typ, freq in self._extract_freqs(repeater):
                band = self.db.gues_band(freq)
                if band not in bands:
                    continue
                if not band.name in freqs:
                    freqs[band.name] = {}
                freqs[band.name][typ] = freq

            fats = []
            for band in freqs:
                if not all([freqs[band].get('tx'), freqs[band].get('rx')]):
                    log.warning('Skipping repeater %s (cross-band)', call)
                    continue

                fat = self.db.add_fat(
                    f_tx=freqs[band]['tx'],
                    f_rx=freqs[band]['rx'],
                    t_tx=tones['tx'],
                    t_rx=tones['rx']
                )
                fats.append(fat)

            self.db.add_repeater(
                call=call,
                active=repeater.find('statusInt').text == '1',
                country_short=repeater.find('country').text.upper(),
                modes=modes,
                fats=fats
            )

            if i % 100 == 0:  # print progress once a while
                sys.stdout.write('\rRepeaters records loaded: '+ str(i))
        print()

    def load_sp5kab_members(self):
        """Load SP5KAB members list from club site."""
        selector = '.entry-content li'
        members = []
        parser = pq(self.DATA['kab'])
        for member in map(lambda li: li.text.split(), parser(selector)):
            if len(member) > 1:
                members.append(member[-1])

        if members:
            self.db.store(
                key='sp5_kab_members',
                val=",".join(members)
            )

if __name__ == '__main__':
    DbUpdater(secret.DB_CREDENTIALS)
