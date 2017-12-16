from requests import get
from collections import namedtuple

from flask import Flask, Response

URL = "http://dmr.ham-digital.net/user_by_call.php?id=260"

DmrRecord = namedtuple("DMRrec", "num,callsign,dmrid,name,country,ctry")

PREFIXY = ("SP", "SO", "SQ")

app = Flask(__name__)


def get_records(url):
    r = get(url)
    if r.status_code != 200:
        return None

    for line in r.text.split("\r\n")[1:]:
        items = list(filter(None, line.split(";")))
        if len(items) < 6:
            continue
        yield DmrRecord(*items)


def sito(records):
    return filter(lambda r: r.callsign[0:2] in PREFIXY, records)


def save4gd77(records):
    head = "Number,Name,Call ID,Type,Ring Style,Call Receive Tone\r\n"
    line = "{num},{name},{dmrid},Private Call,On,1\r\n"
    buf = [head]
    for i, r in enumerate(records):
        buf.append(line.format(
            num=i,
            name=r.callsign + ' ' + r.name,
            dmrid=r.dmrid
        ))

    return buf

@app.route("/", methods=["GET"])
def index():
    recs = sito(get_records(URL))
    recs_sorted = sorted(recs, key=lambda r: r.callsign[3:])
    buf = save4gd77(recs_sorted)
    return Response(
        buf,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=gd77-contacts.csv"}
    )

