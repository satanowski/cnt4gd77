#
# Copyright 2017 by Satanowski
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

Copyright (C) 2017 Satanowski <satanowski@gmail.com>
License: GNU AGPLv3
"""

from collections import namedtuple
from itertools import product

from requests import get
from flask import Flask, Response, render_template, request


class DrsDMRConverter:
    """Process raw CSV from ham-digital."""

    URL = "http://dmr.ham-digital.net/user_by_call.php?id=260"
    DMRRecord = namedtuple("DMRrec", "num,callsign,dmrid,name,country,ctry")
    PREFIXY = "HF,SN,SO,SP,SQ,3Z"
    IMPORTANT_TGS = [
        ('DMR Global', 1),
        ('DMR Local', 9),
        ('SP TG', 260),
        ('SP1 TG', 2601),
        ('SP2 TG', 2602),
        ('SP3 TG', 2603),
        ('SP4 TG', 2604),
        ('SP5 TG', 2605),
        ('SP6 TG', 2606),
        ('SP7 TG', 2607),
        ('SP8 TG', 2608),
        ('SP9 TG', 2609),
        ('Echo', 260097)
    ]

    def __init__(self):
        self.records = []
        self._get_records()

    def _get_records(self):
        """Retrieve CSV file from DMR site."""
        result = get(self.URL)
        if result.status_code != 200:
            self.records = []

        for line in result.text.split("\r\n")[1:]:
            items = list(filter(None, line.split(";")))
            if len(items) < 6:
                continue
            self.records.append(self.DMRRecord(*items))

    def _sieve(self, query):
        """Filter by given prefixes."""
        query = query.split(',')
        prefixes = list(filter(str.isalpha, query)) or self.PREFIXY.split(',')
        areas = list(filter(str.isdigit, query)) or list(map(str, range(1,10)))
        selected = list(map(lambda x: x[0]+x[1], product(prefixes, areas)))
        print("DEBUG:", selected)
        return filter(lambda r: r.callsign[0:3] in selected, self.records)

    def as_csv(self, query):
        """Convert to CSV file accepted by GD-77 software."""
        head = "Number,Name,Call ID,Type,Ring Style,Call Receive Tone\r\n"
        line = "{num},{name},{dmrid:0>8},{type},On,1\r\n"
        buf = [head]

        for i, record in enumerate(self.IMPORTANT_TGS):
            name, dmrid = record
            buf.append(line.format(
                num=i,
                name=name,
                dmrid=dmrid,
                type="Group All"
            ))
        offset = len(self.IMPORTANT_TGS)
        records = sorted(
            self._sieve(query),
            key=lambda r: r.callsign[2:]
        )

        for i, record in enumerate(records):
            buf.append(line.format(
                num=i + offset,
                name=record.callsign + ' ' + record.name,
                dmrid=record.dmrid,
                type="Private Call"
            ))

        return buf


app = Flask(__name__)  # pylint: disable=C0103
dmr = DrsDMRConverter()  # pylint: disable=C0103

@app.route("/", methods=["GET"])
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route("/csv", methods=["GET"])
def get_csv_file():
    """Serve the file."""
    return Response(
        dmr.as_csv(request.args.get('q')),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=gd77-contacts.csv"}
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0')
