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


log.basicConfig(level=log.DEBUG)

class ChannelsFactory:
    """Process raw CSV from ham-digital."""

    ChannelRecord = namedtuple(
        "ChannelRecord",
        "name,rx_freq,tx_freq,mode,power,rx_tone,tx_tone,color,rx_group"\
        ",contact,slot"
    )

    def __init__(self, repeaters, supported_bands, kab_channels):
        self.records = []
        self.repeaters = repeaters
        self.supported_bands = supported_bands
        self.kab_channels = kab_channels

    @staticmethod
    def _filter_rxtx(freqs, is_rx=True):
        return filter(lambda r: (is_rx and 'rx' or 'tx') in r, freqs)

    @staticmethod
    def _is_in_band(frequency, boundaries):
        if not isinstance(frequency, float):
            freq = float(frequency)
        else:
            freq = frequency

        return freq >= boundaries[0] and freq <= boundaries[1]

    def _is_2m(self, freq):
        return self._is_in_band(freq, (144.0, 146.0))

    def _is_70cm(self, freq):
        return self._is_in_band(freq, (430.0, 440.0))

    def filter_rep_freqs(self, freqs: list, band: str):
        """Exctract correct frequencies from repeater record."""
        rxs = map(lambda r: r.get('rx', 0), self._filter_rxtx(freqs))
        txs = map(
            lambda r: r.get('tx', 0),
            self._filter_rxtx(freqs, False)
        )

        if band.lower() == '2m':
            frx = list(filter(self._is_2m, rxs))
            ftx = list(filter(self._is_2m, txs))
        elif band.lower() == '70cm':
            frx = list(filter(self._is_70cm, rxs))
            ftx = list(filter(self._is_70cm, txs))
        else:
            return {}

        if not all([frx, ftx]):
            return {}

        return {
            'rx': frx[0],
            'tx': ftx[0]
        }

    @staticmethod
    def duplicate_channel(channel, updated):
        """Return a copy of tuple with fields changed accordingly to 'updated'
        dict."""
        orig = dict(channel._asdict())
        orig.update(updated)
        return ChannelsFactory.ChannelRecord(**orig)


    def add_repeater(self, repeater, query, digi_reps, anal_reps, sack):
        """Create repeater record and add it to relevant list."""
        band_match = any([
            band.upper() in repeater.bands for band in query['bands']
        ])

        mode_match = any([
            mode.upper() in repeater.modes for mode in query['modes']
        ])

        area_match = any([
            repeater.sign.startswith("SR{}".format(area)) for area
            in query['areas']
        ])

        if not all([band_match, mode_match, area_match]):
            return

        for band in query['bands']: # one channel for each band
            if band.lower() not in self.supported_bands:
                continue

            freqs = self.filter_rep_freqs(repeater.freqs, band)
            if not freqs:  # skip if frew does not match the band
                continue

            if 'CTCSS' in repeater.activation:
                tx_tone = repeater.tones.get('tx', 'None')
                rx_tone = repeater.tones.get('rx', 'None')
            else:
                tx_tone = rx_tone = 'None'

            digital = "MOTOTRBO" in repeater.modes

            channel = ChannelsFactory.ChannelRecord(
                name=repeater.sign,
                rx_freq=freqs['tx'],
                tx_freq=freqs['rx'],
                mode="Digital" if digital else "Analog",
                power='High',
                rx_tone=tx_tone,
                tx_tone=rx_tone,
                color=1 if digital else 0,
                rx_group=1,
                contact=1,
                slot=1
            )

            if digital and query['digi_double']: # additional channel for 2 slot
                channel2 = ChannelsFactory.duplicate_channel(
                    channel,
                    {'name': channel.name + " [2]", 'slot': 2}
                )

                channel = ChannelsFactory.duplicate_channel(
                    channel,
                    {'name': repeater.sign + ' [1]'}
                )

            if query['digi_first']:
                if digital:
                    digi_reps.append(channel)
                    if query['digi_double']:
                        digi_reps.append(channel2)
                else:
                    anal_reps.append(channel)
            else:
                sack.append(channel)
                if digital and query['digi_double']:
                    sack.append(channel2)


    def add_repeaters(self, query: dict):
        """Add Repeaters by given criterion."""
        digital_reps = []
        analog_reps = []
        sack = []

        for repeater in self.repeaters:
            self.add_repeater(repeater, query, digital_reps, analog_reps, sack)

        if query['digi_first']:
            self.records.extend(digital_reps)
            self.records.extend(analog_reps)
        else:
            self.records.extend(sack)

    def add_regular_freqs(self, name: str, freqs: list):
        """Add analog channel."""
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

    def add_kab_specials(self, channel_names):
        """Add chosen KAB channels to the list"""
        self.records.extend(list(
            filter(lambda ch: ch.name in channel_names, self.kab_channels)
        ))


    def as_csv(self, query_json: dict):
        """Convert to CSV file accepted by GD-77 software."""
        head = "Number,Name,Rx Freq,Tx Freq,Ch Mode,Power,Rx Tone,Tx Tone,"\
               "Color Code,Rx Group List,Contact,Repeater Slot\r\n"

        line = "{number},{name},\"{rx_freq:0<9}\",\"{tx_freq:0<9}\",{mode},{power},"\
               "\"{rx_tone}\",\"{tx_tone}\",{color},{rx_group},{contact},{slot}\r\n"
        buf = [head]

        self.records.clear()

        #add KAB spec channels
        kab_spec_ch2add = query_json.get('services', {}).get('spec_kab', [])
        if kab_spec_ch2add:
            self.add_kab_specials(kab_spec_ch2add)

        # add repeaters
        rep = query_json.get('repeaters', {})
        self.add_repeaters({
            'bands': rep.get('bands', []),
            'modes': rep.get('modes', []),
            'areas': rep.get('areas', []),
            'digi_first': rep.get('digi_first', True),
            'digi_double': rep.get('digi_double')
        })

        # add gov services
        services = query_json.get('services', {})
        if 'spec_kab' in services:
            services.pop('spec_kab')

        for service in services:
            self.add_regular_freqs(service, services.get(service, []))

        # add PMR
        self.add_regular_freqs('PMR', query_json.get('apmr', []))
        # add digital PMR
        self.add_regular_freqs('PMR Digi', query_json.get('dpmr', []))

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
