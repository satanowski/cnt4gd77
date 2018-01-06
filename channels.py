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
channels.py

Copyright (C) 2017-2018 Satanowski <satanowski@gmail.com>
License: GNU AGPLv3
"""

import logging as log
from collections import namedtuple, OrderedDict

from przemienniki import PrzemienikiWrapper
import utils

log.basicConfig(level=log.DEBUG)

class ChannelsFactory:
    """Process raw CSV from ham-digital."""

    ChannelRecord = namedtuple(
        "ChannelRecord",
        "name,rx_freq,tx_freq,mode,power,rx_tone,tx_tone,color,rx_group"\
        ",contact,slot"
    )

    def __init__(self):
        self.records = OrderedDict()


    def as_csv(self, query_json: dict):
        """Convert to CSV file accepted by GD-77 software."""
        head = "Number,Name,Rx Freq,Tx Freq,Ch Mode,Power,Rx Tone,Tx Tone,"\
               "Color Code,Rx Group List,Contact,Repeater Slot\r\n"

        line = "{number},{name},{rx_freq},{tx_freq},{mode},{power},{rx_tone},{tx_tone},{color},{rx_group},{contact},{slot}\r\n"
        buf = [head]


        # for i, rec_id in enumerate(records_set):
        #     record = records_set[rec_id]
        #     buf.append(line.format(
        #         ...
        #     ))

        return buf