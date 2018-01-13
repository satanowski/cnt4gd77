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
import io
import zipfile
from datetime import datetime

from flask import Flask, Response, render_template, abort
import msgpack

from contacts import ContactsFactory
from channels import ChannelsFactory
import utils

now = datetime.now()
__VERSION__ = 0,9,3
__LAST_UPDATE__ = "2018-01-13"
__LAST_DATA_UPDATE__ = "{d} {h}:{m}".format(
    d=now.date().isoformat(),
    h=now.time().hour,
    m=now.time().minute
)


utils.load_config()

log.basicConfig(level=log.DEBUG)

app = Flask(__name__)  # pylint: disable=C0103
contacts = ContactsFactory()  # pylint: disable=C0103
channels = ChannelsFactory()  # pylint: disable=C0103

flasklog = log.getLogger('werkzeug')
flasklog.setLevel(log.ERROR)

@app.route("/", methods=["GET"])
def index():
    """Serve the main page."""
    return render_template(
        'index.html',
        prefixy=utils.CONFIG['sp_prefixy'],
        sp_talkgroups=utils.CONFIG['sp_talk_groups'],
        additionals=utils.CONFIG['additional_contacts'],
        additional_tgs=utils.CONFIG['additional_talkgroups'],
        bands=utils.REPS.bands,
        modes=utils.REPS.modes,
        bands_supported=utils.CONFIG['supported_bands'],
        modes_supported=utils.CONFIG['supported_modes'],
        gov_services=utils.CONFIG['gov_services'],
        pmr=utils.CONFIG['pmr'],
        version='.'.join(map(str, list(__VERSION__))),
        last_update=__LAST_UPDATE__,
        last_data=__LAST_DATA_UPDATE__
    )


@app.route("/csv/<query>", methods=["GET"])
def get_csv_file(query):
    """Serve the file."""
    try:
        query = msgpack.unpackb(bytearray.fromhex(query), encoding='utf-8')
        # log.debug(query)
    except (msgpack.exceptions.UnpackValueError, ValueError) as error:
        log.error("Wrong query: %s", error)
        abort(404)

    contacts_csv = contacts.as_csv(query['contacts'])
    if utils.are_channels_requested(query):
        channels_csv = channels.as_csv(query['channels'])
        a_mem_file = io.BytesIO()
        with zipfile.ZipFile(a_mem_file,'w') as zip_file:
            zip_file.writestr('contacts.csv', ''.join(contacts_csv))
            zip_file.writestr('channels.csv', ''.join(channels_csv))

        return Response(
            a_mem_file.getvalue(),
            mimetype="application/zip",
            headers={"Content-disposition": "attachment; filename=gd77.zip"}
        )

    return Response(
        contacts_csv,
        mimetype="text/csv",
        headers={
            "Content-disposition": "attachment; filename=gd77-contacts.csv"
        }
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
