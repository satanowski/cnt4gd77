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
import os
import zipfile
from datetime import datetime

from flask import Flask, Response, render_template, abort, session, redirect, \
                  url_for
import msgpack

from contacts import ContactsFactory
from channels import ChannelsFactory
from repeaters import PrzemiennikiWrapper
import utils
import secret

now = datetime.utcnow()
__VERSION__ = 0,9,6
__LAST_UPDATE__ = "2018-01-21"
__LAST_DATA_UPDATE__ = "{d} {h:02d}:{m:02d}".format(
    d=now.date().isoformat(),
    h=now.time().hour,
    m=now.time().minute
)

EXT_DATA = utils.load_external_data()
utils.load_config(EXT_DATA['kab'])

log.basicConfig(level=log.DEBUG)

app = Flask(__name__)  # pylint: disable=C0103
app.secret_key = os.urandom(32)
contacts = ContactsFactory(EXT_DATA['dmr'])  # pylint: disable=C0103
repeaters = PrzemiennikiWrapper(EXT_DATA['rep']) # pylint: disable=C0103
channels = ChannelsFactory(repeaters, utils.CONFIG['supported_bands'])  # pylint: disable=C0103

EXT_DATA = None  # No need to keep it
del EXT_DATA

flasklog = log.getLogger('werkzeug')
flasklog.setLevel(log.ERROR)


@app.route("/", methods=["GET"])
def index():
    """Serve the main page."""

    html_header=render_template('header.html',
        kab_user=session.get('kab_user', False)
    )

    prefixy=render_template('prefixy.html', prefixy=utils.CONFIG['sp_prefixy'])

    talkgroups=render_template('talkgroups.html',
        sp_talkgroups=utils.CONFIG['sp_talk_groups'],
        additional_tgs=utils.CONFIG['additional_talkgroups']
    )

    spec_contacts=render_template('spec_contacts.html',
        additionals=utils.CONFIG['additional_contacts']
    )

    chan_repeaters=render_template('repeaters.html',
        bands=repeaters.bands,
        modes=repeaters.modes,
        bands_supported=utils.CONFIG['supported_bands'],
        modes_supported=utils.CONFIG['supported_modes']
    )

    chan_services=render_template('gov_services.html',
        gov_services=utils.CONFIG['gov_services']
    )

    chan_pmr=render_template('pmr.html',
        pmr=utils.CONFIG['pmr'],
        pmr_digi=utils.CONFIG['pmr-digi']
    )

    chan_kab=render_template('kab.html',
        kab_channels=secret.SPEC_KAB_CHANNELS
    )

    channels=render_template('channels.html',
        repeaters=chan_repeaters,
        gov_services=chan_services,
        pmr=chan_pmr,
        kab_user=session.get('kab_user', False),
        kab_channels=chan_kab
    )

    modal_info=render_template('modal_info.html',
        version='.'.join(map(str, list(__VERSION__))),
        last_update=__LAST_UPDATE__,
        last_data=__LAST_DATA_UPDATE__
    )

    return render_template('index.html',
        top_panel=render_template('top_panel.html'),
        generate=render_template('generate.html'),
        comments=render_template('comments.html'),
        footer=render_template('footer.html'),
        error=render_template('error.html'),
        html_header=html_header,
        prefixy=prefixy,
        talkgroups=talkgroups,
        spec_contacts=spec_contacts,
        channels=channels,
        modal_info=modal_info,
        kab_mode=session.get('kab_user', False)
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

@app.route('/static/<path:path>')
def getStaticFile(path):
    return send_from_directory('static', path, cache_timeout=0)


@app.route('/kab/<hash_sting>', methods=['GET'])
def kab_login(hash_sting:str):
    if hash_sting in secret.SECRET_LIST:
        session['kab_user'] = True
    return redirect(url_for('index'))


@app.route('/out', methods=['GET'])
def kab_logout():
    session.pop('kab_user', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
