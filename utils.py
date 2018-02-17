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

import logging as log
from datetime import datetime

import fetcher

log.basicConfig(level=log.DEBUG)

def load_external_data():
    """Just a helper function to avoid import loop."""
    return fetcher.fetch_urls()


def are_channels_requested(query):
    """Check if user requested any channel."""
    any_repeater = any(query.get('channels', {}).get('repeaters', {}).values())
    any_service = any(query.get('channels', {}).get('services', {}).values())
    any_pmr = query.get('channels', {}).get('pmr', False)

    return any([any_repeater, any_service, any_pmr])


def current_date_as_string():
    """Convert current time into desired string."""
    now = datetime.utcnow()
    return "{d} {h:02d}:{m:02d}".format(
        d=now.date().isoformat(),
        h=now.time().hour,
        m=now.time().minute
    )

def disable_flask_log():
    """Disable flask log messages."""
    flasklog = log.getLogger('werkzeug')
    flasklog.setLevel(log.ERROR)


def fix_country(country: str) -> str:
    """Correct name of the country."""
    remap = {
        'Argentina Republic': 'Argentina',
        'Moldava': 'Czech Republic',
        'Swasiland': 'Swaziland',
        'Viet Nam': 'Vietnam',
        'AUS': 'Australia',
        'BRA': 'Brazil',
        'CAN': 'Canada',
        'CHN': 'China',
        'DNK': 'Denmark',
        'IMN': 'Isle od Man',
        'MEX': 'Mexico',
        'NZL': 'New Zealand',
        'THA': 'Thailand',
        'TWN': 'Taiwan',
        'United States': 'USA',
        'Korsika': 'France',
        'Netherlands Antilles': 'Netherlands',
        'New Zeland': 'New Zealand'
    }

    part_remap = {
        'Belarus': 'Belarus',
        'Bosnia and': 'Bosnia and Hercegovina',
        'Dominic': 'Dominican Republic',
        'Domenican': 'Dominican Republic',
        'Korea': 'Korea',
        'Macao': 'China',
        'Oesterreich': 'Austria'
    }

    if country in remap:
        return remap[country]

    for string in part_remap:
        if country.startswith(string):
            return part_remap[string]

    return country
