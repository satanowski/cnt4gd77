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
CSV converter hamdigital <-> gd-77

Copyright (C) 2017-2018 Satanowski <satanowski@gmail.com>
License: GNU AGPLv3
"""

from collections import namedtuple, OrderedDict
from itertools import product
import logging as log
import re

import utils

log.basicConfig(level=log.DEBUG)


class ContactsFactory:
    """Process raw CSV from ham-digital."""

    ContactRecord = namedtuple(
        "ContactRecord",
        "num,callsign,dmrid,name,country,ctry"
    )

    def __init__(self, csv_raw_content):
        self.records = {}
        self.ignored_contacts = []
        self._get_records(csv_raw_content)

    def _get_records(self, csv_raw_content):
        """Extract data from CSV and save them as dict of records."""
        for line in csv_raw_content.split("\r\n")[1:]:
            items = list(map(str.strip, filter(None, line.split(";"))))
            if len(items) < 6:
                continue
            dmr_rec = self.ContactRecord(*items)
            self.records[dmr_rec.dmrid] = dmr_rec

    def _sieve(self, prefixes, areas):
        """Filter by given prefixes."""
        selected = list(
            map(lambda x: x[0]+x[1], product(prefixes, map(str, areas)))
        )

        return filter(  # returns DMR ids of selected records
            lambda r: self.records[r].callsign[0:3] in selected,
            self.records
        )

    @staticmethod
    def _read_special_group(name):
        # special case for SP5KAB
        if name.lower() == 'sp5kab':
            group = utils.CONFIG['sp5kab']
        else:
            group = utils.CONFIG.get(name)

        if not group:
            return None

        return sorted(group, key=lambda sign: sign[2:])

    def _get_rec_by_call(self, callsign):
        for rec in self.records:
            if self.records[rec].callsign == callsign:
                return self.records[rec]
        return None

    def _get_rec_by_id(self, dmr_id):
        return self.records.get(dmr_id, None)

    def _simple_dmr_rec(self, dmrid: str, name: str):
        return self.ContactRecord(
            num=0,
            callsign=name.strip(),
            dmrid=str(dmrid).strip(),
            name='',
            country='',
            ctry=''
        )

    def add_additional_contacts_numeric(self, rec_set: dict,
                                        additionals: list):
        """From given list of additional contacts filter these that are numeric
        and are present in config file. Add them to given rec_set dict."""
        records_to_add = filter(
            lambda r: str(r['id']) in additionals and str(r['id']).isnumeric(),
            utils.CONFIG['additional_contacts']
        )

        for record in records_to_add:
            if record['id'] in self.ignored_contacts:
                continue
            rec_set[record['id']] = self._simple_dmr_rec(record['id'],
                                                         record['name'])


    def add_priority_contacts(self, rec_set: dict, prio_list: str):
        """From given string, exctract list of call sign and add them to
        rec_set if they exists in main DMR list."""

        for contact in map(str.upper, re.split('[,|.| |;]', prio_list)):
            if contact.isnumeric() and contact in self.records: # just dmr id
                rec_set[contact] = self.records[contact]
            else:  # call sign
                rec = self._get_rec_by_call(contact)
                if rec:
                    rec_set[rec.dmrid] = rec

    def add_additional_contacts_alpha(self, rec_set: dict, additionals: list):
        """Add additional contacts by name of its group (defined in config)."""
        for addrec in filter(lambda r_id: r_id.isalnum(), additionals):
            spec_group = self._read_special_group(addrec)
            if not spec_group:
                continue
            for callsign in spec_group:
                if callsign in self.ignored_contacts:
                    continue
                rec = self._get_rec_by_call(callsign)
                if rec:
                    rec_set[rec.dmrid] = rec

    def add_areatalkgroups(self, rec_set: dict, tg_list: list):
        """Add TG for areas."""

        available_tgs = sorted(
            utils.CONFIG['sp_talk_groups'].get('items', []) +
            utils.CONFIG['additional_talkgroups'],
            key=lambda r: r['id']
        )

        for tg_id in map(int, tg_list):
            a_tg = list(filter(lambda r: r['id'] == tg_id, available_tgs))
            if not a_tg:
                continue

            rec_set[a_tg[0]['id']] = \
                self._simple_dmr_rec(a_tg[0]['id'], a_tg[0]['name'])

    def add_contacts_by_area_and_prefix(self, rec_set: dict, prfxs: list,
                                        areas: list):
        """Add contacts by area and callsign prefix."""
        rec_ids_sorted = sorted(
            self._sieve(prfxs, areas),
            key=lambda rid: self.records[rid].callsign[2:]
        )

        for rec_id in filter(lambda rec_id: rec_id not in rec_set,
                             rec_ids_sorted):
            a_record = self.records[rec_id]
            if a_record.callsign in self.ignored_contacts:
                continue
            rec_set[rec_id] = a_record


    def as_csv(self, query_json: dict):
        """Convert to CSV file accepted by GD-77 software."""
        head = "Number,Name,Call ID,Type,Ring Style,Call Receive Tone\r\n"
        line = "{num},{name},{dmrid:0>8},{type},On,1\r\n"
        buf = [head]

        records_set = OrderedDict()
        self.ignored_contacts = list(map(
            str.upper,
            re.split('[,|.| |;]', query_json.get('igno', ""))
        ))

        self.add_additional_contacts_numeric(records_set, query_json['adds'])
        self.add_areatalkgroups(records_set, query_json['tgs'] or [])
        self.add_priority_contacts(records_set, query_json['prio'])
        self.add_additional_contacts_alpha(records_set, query_json['adds'])
        if all(map(query_json.get, ['sp_area', 'sp_prefix'])):
            self.add_contacts_by_area_and_prefix(
                records_set,
                query_json.get('sp_prefix'),
                query_json.get('sp_area')
            )

        for i, rec_id in enumerate(records_set):
            record = records_set[rec_id]
            buf.append(line.format(
                num=i,
                name=' '.join([record.callsign, record.name]).strip(),
                dmrid=record.dmrid,
                type="Group All" if len(record.dmrid) <= 5 else "Private Call"
            ))

        return buf
