"""
db
"""
import logging as log
from uuid import uuid1
from hashlib import md5

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
    Band, Base, Channel, ChannelGroup, Country, Dmr, FaT, Mode, Prefix,
    Repeater, Store, TgGroup, Token
)


class DB():
    """Operation on DB."""

    def __init__(self, credentials, echo=False):
        self.engine = create_engine(credentials, echo=echo)
        self.base = Base
        self.base.metadata.create_all(self.engine, checkfirst=True)
        session = sessionmaker(bind=self.engine)
        self.session = session()

        if not self._exists(TgGroup, 'id', 0):
            self.session.add(TgGroup(id=0, name="<no group>"))
            self.session.commit()
        if not self._exists(ChannelGroup, 'id', 0):
            self.session.add(ChannelGroup(id=0, name="<no group>"))
            self.session.commit()

    def store(self, key, val):
        """Store or update key:val record."""
        rec = self.one_or_none(Store, 'name', key)
        if not rec:
            rec = Store(name=key, value=val)
            self.session.add(rec)
        else:
            rec.value = val
        self.session.commit()

    def one_or_none(self, model, field_name: str, value):
        """Return record of given model or None if it does not exists."""
        return self.session.query(model).filter(
            getattr(model, field_name) == value
        ).one_or_none()

    def _exists(self, model, field_name: str, value: str) -> bool:
        return self.one_or_none(
            model,
            getattr(model, field_name),
            value
        ).one_or_none() != None

    def add_countries(self, countries_list: list):
        """Populate Country table."""
        for name, abbrev in countries_list:
            country = self.one_or_none(Country, 'short', abbrev.upper())
            if country:
                country.name = name
            else:
                self.session.add(Country(name=name, short=abbrev.upper()))
        self.session.commit()

    def add_prefixes(self, c_short: str, prfxs: list, amin: int, amax: int):
        """Add Prefix records for given country."""
        country = self.one_or_none(Country, 'short', c_short)

        if not country:
            log.error('No such country: %s!', c_short)
            return

        for prefix in prfxs:
            if self._exists(Prefix, 'name', prefix):
                continue
            self.session.add(Prefix(name=prefix, country_id=country.id))

        country.area_min = amin
        country.area_max = amax
        self.session.commit()

    def add_band(self, name: str, supported: bool, low: float, high: float):
        """Add Band record."""
        band = self.one_or_none(Band, 'name', name)
        if band:
            band.supported = supported
            band.low = low
            band.high = high
        else:
            self.session.add(
                Band(name=name, supported=supported, low=low, high=high)
            )
        self.session.commit()

    def add_mode(self, name: str, ident: str, indict: str, supported: bool):
        """Add Mode record."""
        mode = self.one_or_none(Mode, 'name', name)
        if mode:
            mode.ident = ident
            mode.indicator = indict
            mode.supported = supported
        else:
            self.session.add(
                Mode(name=name, ident=ident, indicator=indict, supported=supported)
            )
        self.session.commit()

    def _country_id_by_short(self, country_short: str) -> int:
        """Determine Country by its short name."""
        country = self.one_or_none(Country, 'short', country_short)
        return country.id if country else 0

    def add_dmr(self, dmr_id: int, call: str, name: str, is_talk_group: bool,
                country_short: str, description: str, tg_group=0):
        """Add DMR record."""

        dmr = self.one_or_none(Dmr, 'dmr_id', dmr_id)

        if dmr:
            dmr.name = name
            dmr.call = call
            dmr.is_tg = is_talk_group
            dmr.country_id = self._country_id_by_short(country_short)
            dmr.description = description
            dmr.tg_group_id = tg_group

        else:
            dmr = Dmr(
                dmr_id=dmr_id,
                name=name,
                call=call,
                is_tg=is_talk_group,
                country_id=self._country_id_by_short(country_short),
                description=description,
                tg_group_id=tg_group
            )
            self.session.add(dmr)

        self.session.commit()

    def add_tg_group(self, name: str, description: str, members: list):
        """Add TG Group record."""
        tgg = self.one_or_none(TgGroup, 'name', name)
        if not tgg:
            tgg = TgGroup(name=name, description=description)
            self.session.add(tgg)
            self.session.commit()

        for dmr_id in members:
            dmr = self.one_or_none(Dmr, 'dmr_id', dmr_id)
            if not dmr:
                continue
            dmr.tg_group_id = tgg.id
        self.session.commit()

    def add_channel(self, name: str, comment: str, is_digit: bool, slot: int,
                    fat_id: int, group_id: int):
        """Add Channel record."""
        chan = self.one_or_none(Channel, 'name', name)
        if chan:
            chan.comment = comment
            chan.is_digit = is_digit
            chan.slot = slot
            chan.fat_id = fat_id
            chan.group_id = group_id
        else:
            self.session.add(Channel(
                name=name,
                comment=comment,
                is_digit=is_digit,
                slot=slot,
                fat_id=fat_id,
                group_id=group_id
            ))

        self.session.commit()

    def gues_band(self, freq: float):
        """Detect the band on the base of given frequency."""
        return self.session.query(Band).filter(
            Band.low <= freq,
            Band.high >= freq
        ).one_or_none()

    def add_fat(self, f_tx: float, f_rx: float, t_tx: float, t_rx: float):
        """Add Frequency and Tone record."""
        band = self.gues_band(f_tx)
        if not band:
            return None

        fat = self.session.query(FaT).filter(
            FaT.f_tx == f_tx and
            FaT.f_rx == f_rx and
            FaT.t_tx == t_tx and
            FaT.t_rx == t_rx).one_or_none()

        if not fat:
            fat = FaT(
                f_tx=f_tx,
                f_rx=f_rx,
                t_tx=t_tx,
                t_rx=t_rx,
                band_id=band.id
            )
            self.session.add(fat)
            self.session.commit()

        return fat

    def add_channel_group(self, name: str, description: str, is_digit: bool,
                          members: list, slot=1):
        """Add channel group record and its members."""
        chg = self.one_or_none(ChannelGroup, 'name', name)

        if chg:
            chg.description = description
        else:
            chg = ChannelGroup(name=name, description=description)
            self.session.add(chg)

        self.session.commit()

        for i, freq in enumerate(members):
            self.add_channel(
                name='{} {}'.format(name, i),
                comment='',
                is_digit=is_digit,
                slot=slot,
                fat_id=self.add_fat(freq, freq, 0, 0).id,
                group_id=chg.id
            )

    def add_token(self, owner: str, active: bool):
        """Add Token record."""
        tkn = self.one_or_none(Token, 'owner', owner)
        if tkn:
            tkn.token = md5(uuid1().bytes).hexdigest()
            tkn.active = active
        else:
            tkn = Token(
                token=md5(uuid1().bytes).hexdigest(),
                owner=owner,
                active=active
            )
            self.session.add(tkn)

        self.session.commit()

    def get_countries_dict(self):
        """Return list of defined countries as dict."""
        return {
            name: short for name, short in
            self.session.query(Country.name, Country.short).all()
        }

    def get_mode_by_ident(self, ident):
        """Get Mode record by its identificator."""
        qry = self.session.query(Mode).filter(Mode.ident == ident)
        return qry.one_or_none()

    def add_repeater(self, call: str, active: bool, country_short: str,
                     modes: list, fats: list):
        """Add of update Repeater."""
        rep = self.one_or_none(Repeater, 'call', call)
        if not rep:
            rep = Repeater(
                call=call,
                country_id=self._country_id_by_short(country_short),
                active=active
            )
            self.session.add(rep)
        rep.modes.extend(modes)
        rep.fats.extend(fats)

        self.session.commit()
