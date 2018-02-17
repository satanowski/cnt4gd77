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
DB init

Copyright (C) 2017-2018 Satanowski <satanowski@gmail.com>
License: GNU AGPLv3
"""

import json
import logging as log
from pathlib import Path


import secret
from utils import current_date_as_string
from db import DB


log.basicConfig(level=log.DEBUG)
LOAD_LIST = []

def register4load(func):
    """Simple func decorator."""
    LOAD_LIST.append(func.__name__)
    return func


class DbInitialize():
    """Iniatilze DB with static data."""

    def __init__(self, credentials):
        self.db = DB(credentials)
        for loader in LOAD_LIST:  # order does matter
            getattr(self, loader)()

        self.db.store('db_created', current_date_as_string())

    @staticmethod
    def _load(data_file, callback):
        """Load json file and run a given function of loaded data."""
        path = (Path.cwd() / 'data' / data_file).with_suffix('.json')
        try:
            callback(json.loads(path.read_text()))
        except (IOError, ValueError) as error:
            log.error('Cannot read file %s!\n%s', path, error)

    @register4load
    def load_countries(self):
        """Import list of countries."""
        self._load('countries', self.db.add_countries)

    @register4load
    def load_prefixes(self):
        """Import list of call sign prefixes."""
        def func(data):  # pylint: disable=C0111
            for country_short, specs in data.items():
                self.db.add_prefixes(
                    c_short=country_short,
                    prfxs=specs.get('list', []),
                    amin=specs.get('min'),
                    amax=specs.get('max')
                )

        self._load('prefixes', func)

    @register4load
    def load_bands(self):
        """Import bands data."""
        def func(data):  # pylint: disable=C0111
            for name, (sup, low, high) in data.items():
                self.db.add_band(
                    name=name,
                    supported=(sup == 1),
                    low=low,
                    high=high
                )

        self._load('bands', func)

    @register4load
    def load_modes(self):
        """Import modes data."""
        def func(data):  # pylint: disable=C0111
            for name, specs in data.items():
                self.db.add_mode(
                    name=name,
                    ident=specs.get('id', name).lower(),
                    indict=specs.get('indicator', None),
                    supported=specs.get('supported', 0) == 1
                )

        self._load('modes', func)

    @register4load
    def load_fixed_dmr_contacts(self):
        """Import list of fixed contacts."""
        def func(data):  # pylint: disable=C0111
            for contact in data:
                self.db.add_dmr(
                    dmr_id=int(contact.get('id')),
                    call=contact.get('call'),
                    name=contact.get('name'),
                    is_talk_group=contact.get('istg', 1) == 1,
                    country_short=contact.get('cntr'),
                    description=contact.get('desc')
                )

        self._load('fixed_contacts', func)

    @register4load
    def load_sp_tgs(self):
        """Import polish TGs."""
        def func(data):  # pylint: disable=C0111
            for tg_group in data:
                self.db.add_tg_group(
                    name=tg_group.get('name'),
                    description=tg_group.get('desc'),
                    members=tg_group.get('members')
                )

        self._load('sp_tgs', func)

    @register4load
    def load_channels(self):
        """Import fixed channels TGs."""
        def func(data):  # pylint: disable=C0111
            for channel_group in data:
                self.db.add_channel_group(
                    name=channel_group.get('name'),
                    description=channel_group.get('desc', ''),
                    is_digit=channel_group.get('is_digit', False),
                    members=channel_group.get('freqs', []),
                    slot=channel_group.get('slot', 1)
                )

        self._load('channel_groups', func)

    @register4load
    def load_sp5kab_secret(self):
        """Import private channels for sp5kab members."""
        for channel in secret.SPEC_KAB_CHANNELS:
            fat = self.db.add_fat(
                channel.get('ftx'),
                channel.get('frx'),
                channel.get('ttx'),
                channel.get('trx')
            )
            self.db.add_channel(
                name=channel.get('name'),
                comment='',
                is_digit=channel.get('is_digit'),
                slot=channel.get('slot', 1),
                fat_id=fat.id,
                group_id=0
            )

    @register4load
    def load_tokens(self):
        """Import private channels for sp5kab members."""
        for owner in secret.DEFAULT_TOKENS_OWNERS:
            self.db.add_token(owner, True)

if __name__ == '__main__':
    DbInitialize(secret.DB_CREDENTIALS)
