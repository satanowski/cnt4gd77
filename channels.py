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
from collections import namedtuple

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
        self.records = []

    def _filter_rxtx(self, freqs, rx=True):
        return filter(lambda r: (rx and 'rx' or 'tx') in r, freqs)

    def _is_in_band(self, freq, boundaries):
        if not isinstance(freq, float):
            f = float(freq)
        else:
            f = freq

        return f >= boundaries[0] and f <= boundaries[1]

    def _is_2m(self, freq):
        return self._is_in_band(freq, (144.0, 146.0))

    def _is_70cm(self, freq):
        return self._is_in_band(freq, (430.0, 440.0))

    def filter_rep_freqs(self, freqs:list, band:str):
        """Exctract correct frequencies from repeater record."""
        rxs = map(lambda r: r.get('rx', 0), self._filter_rxtx(freqs))
        txs = map(
            lambda r: r.get('tx', 0),
            self._filter_rxtx(freqs, False)
        )

        if band.lower() == '2m':
            rx = list(filter(lambda f: self._is_2m(f), rxs))
            tx = list(filter(lambda f: self._is_2m(f), txs))
        elif band.lower() == '70cm':
            rx = list(filter(lambda f: self._is_70cm(f), rxs))
            tx = list(filter(lambda f: self._is_70cm(f), txs))
        else:
            return {}

        if not all([rx, tx]):
            return {}

        return {
            'rx': rx[0],
            'tx': tx[0]
        }


    def add_repeaters(self, bands: list, modes: list, areas: list,
                      digi_first: bool):
        """Add Repeaters by given criterion."""
        digital_reps = []
        analog_reps = []
        sack = []

        for repeater in utils.REPS.repeaters:
            band_match = any([band.upper() in repeater.bands for band in bands])
            mode_match = any([mode.upper() in repeater.modes for mode in modes])
            area_match = any([repeater.sign.startswith("SR{}".format(area))
                              for area in areas])

            if all([band_match, mode_match, area_match]):
                for band in bands:
                    if band.lower() not in utils.CONFIG['supported_bands']:
                        continue
                    # one channel for each band
                    freqs = self.filter_rep_freqs(repeater.freqs, band)
                    if not freqs:
                        continue

                    if 'CTCSS' in repeater.activation:
                        tx_tone = repeater.tones.get('tx', 'None')
                        rx_tone = repeater.tones.get('rx', 'None')
                    else:
                        tx_tone = rx_tone = 'None'

                    digital = "MOTOTRBO" in repeater.modes

                    channel = ChannelsFactory.ChannelRecord(
                        name=repeater.sign,
                        rx_freq=freqs['rx'],
                        tx_freq=freqs['tx'],
                        mode="Digital" if digital else "Analog",
                        power='High',
                        rx_tone=rx_tone,
                        tx_tone=tx_tone,
                        color=1 if digital else 0,
                        rx_group=1,
                        contact=1,
                        slot=1
                    )
                    if digi_first:
                        if digital:
                            digital_reps.append(channel)
                        else:
                            analog_reps.append(channel)
                    else:
                        sack.append(channel)
        if digi_first:
            self.records.extend(digital_reps)
            self.records.extend(analog_reps)
        else:
            self.records.extend(sack)

    def add_regular_freqs(self, name:str, freqs: list):
        for i, freq in enumerate(freqs):
            channel = ChannelsFactory.ChannelRecord(
                name="{} {}".format(name, i+1),
                rx_freq=freq,
                tx_freq=freq,
                mode="Analog",
                power='Low',
                rx_tone='None',
                tx_tone='None',
                color=0,
                rx_group=0,
                contact=0,
                slot=1
            )
            self.records.append(channel)


    def as_csv(self, query_json: dict):
        """Convert to CSV file accepted by GD-77 software."""
        head = "Number,Name,Rx Freq,Tx Freq,Ch Mode,Power,Rx Tone,Tx Tone,"\
               "Color Code,Rx Group List,Contact,Repeater Slot\r\n"

        line = "{number},{name},\"{rx_freq:0<9}\",\"{tx_freq:0<9}\",{mode},{power},"\
               "\"{rx_tone}\",\"{tx_tone}\",{color},{rx_group},{contact},{slot}\r\n"
        buf = [head]

        self.records.clear()
        # add repeaters
        rep = query_json.get('repeaters', {})
        self.add_repeaters(
            bands=rep.get('bands', []),
            modes=rep.get('modes', []),
            areas=rep.get('areas', []),
            digi_first=rep.get('digi_first', True)
        )

        # add gov services
        for service in query_json.get('services', []):
            self.add_regular_freqs(
                service,
                query_json.get('services',{}).get(service, [])
            )

        # add PMR
        self.add_regular_freqs('PMR', query_json.get('pmr',[]))

        for i, rec in enumerate(self.records):
            buf.append(line.format(
                number=i,
                name=rec.name,
                rx_freq=str(rec.rx_freq).replace('.', ','),
                tx_freq=str(rec.tx_freq).replace('.', ','),
                mode=rec.mode,
                power=rec.power,
                rx_tone=str(rec.rx_tone).replace('.', ','),
                tx_tone=str(rec.tx_tone).replace('.', ','),
                color=rec.color,
                rx_group=rec.rx_group,
                contact=rec.contact,
                slot=rec.slot
            ))

        return buf
