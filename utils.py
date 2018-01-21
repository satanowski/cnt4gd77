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
utils.py

Copyright (C) 2017-2018 Satanowski <satanowski@gmail.com>
License: GNU AGPLv3
"""

from pathlib import Path
import logging as log

import yaml

import fetcher
from kab import KAB


log.basicConfig(level=log.DEBUG)

CONFIG = {}

EXT_DATA = fetcher.fetch_urls()


def load_config():
    """Load config file."""
    global CONFIG

    path = Path.cwd() / "config.yaml"
    if not path.exists():
        log.error('No config file! Exiting!')
        sys.exit(1)
    try:
        with open(path) as cfg_file:
            config = yaml.load(cfg_file)
            log.debug('Config loaded')
    except IOError:
        log.error('Cannot read config file! Exiting!')
        sys.exit(1)
    if not config:
        log.error('Empty config! Exiting!')
        sys.exit(1)

    CONFIG = config
    CONFIG['supported_modes'] = {
        a:b for a,b in config.get('supported_modes', [])
    }

    CONFIG['sp5kab'] = KAB.retrieve_members(EXT_DATA['kab']) or \
                       config.get('sp5kab', [])


def are_channels_requested(query):
    """Check if user requested any channel."""
    any_repeater = any(query.get('channels',{}).get('repeaters', {}).values())
    any_service = any(query.get('channels',{}).get('services', {}).values())
    any_pmr = query.get('channels',{}).get('pmr', False)

    return any([any_repeater, any_service, any_pmr])
