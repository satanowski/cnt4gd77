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
Lorem ipsum dolor sit amet, consectetur adipiscing elit.

Copyright (C) 2017-2018 Satanowski <satanowski@gmail.com>
License: GNU AGPLv3
"""

import logging as log

from flask import Flask, Response, render_template, abort
import msgpack

from dmr import DrsDMRConverter


log.basicConfig(level=log.DEBUG)

app = Flask(__name__)  # pylint: disable=C0103
dmr = DrsDMRConverter()  # pylint: disable=C0103

@app.route("/", methods=["GET"])
def index():
    """Serve the main page."""
    return render_template(
        'index.html',
        prefixy=dmr.SP_PREFIX_LIST,
        talkgroups=dmr.TALK_GROUPS,
        additionals=dmr.ADDITIONAL_CONTACTS
    )


@app.route("/csv/<query>", methods=["GET"])
def get_csv_file(query):
    """Serve the file."""
    try:
        query = msgpack.unpackb(bytearray.fromhex(query), encoding='utf-8')
    except (msgpack.exceptions.UnpackValueError, ValueError) as error:
        log.error("Wrong query: %s", error)
        abort(404)

    return Response(
        dmr.as_csv(query),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=gd77-contacts.csv"}
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
