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

from requests import get
from flask import Flask, Response

URL = "http://dmr.ham-digital.net/user_by_call.php?id=260"

DmrRecord = namedtuple("DMRrec", "num,callsign,dmrid,name,country,ctry")

PREFIXY = ("HF", "SN", "SO", "SP", "SQ", "3Z")

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


app = Flask(__name__)  # pylint: disable=C0103

def get_records(url):
    """Retrieve CSV file from DMR site."""
    result = get(url)
    if result.status_code != 200:
        yield None

    for line in result.text.split("\r\n")[1:]:
        items = list(filter(None, line.split(";")))
        if len(items) < 6:
            continue
        yield DmrRecord(*items)


def sieve(records, prefixy):
    """Filter by given prefixes."""
    return filter(lambda r: r.callsign[0:2] in prefixy, records)


def save4gd77(records):
    """Convert to CSV file accepted by GD-77 software."""
    head = "Number,Name,Call ID,Type,Ring Style,Call Receive Tone\r\n"
    line = "{num},{name},{dmrid:0>8},{type},On,1\r\n"
    buf = [head]

    for i, record in enumerate(IMPORTANT_TGS):
        name, dmrid = record
        buf.append(line.format(
            num=i,
            name=name,
            dmrid=dmrid,
            type="Group All"
        ))

    for i, record in enumerate(records):
        buf.append(line.format(
            num=i + len(IMPORTANT_TGS),
            name=record.callsign + ' ' + record.name,
            dmrid=record.dmrid,
            type="Private Call"
        ))

    return buf


@app.route("/", methods=["GET"])
def index():
    """Serve the file."""
    recs = sieve(get_records(URL), PREFIXY)
    recs_sorted = sorted(recs, key=lambda r: r.callsign[2:])
    buf = save4gd77(recs_sorted)
    return Response(
        buf,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=gd77-contacts.csv"}
    )
