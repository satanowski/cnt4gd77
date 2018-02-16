"""
models.py
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, \
                       SmallInteger, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class Country(Base):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True, nullable=False)
    short = Column(String(32), unique=True, nullable=False)
    area_min = Column(Integer, nullable=True, default=None)
    area_max = Column(Integer, nullable=True, default=None)

    prefixes = relationship('Prefix', back_populates='country')


class Prefix(Base):
    __tablename__ = 'prefix'

    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)
    country_id = Column(Integer, ForeignKey('country.id'), nullable=False)

    country = relationship('Country', back_populates='prefixes')


class Band(Base):
    __tablename__ = 'band'

    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)
    supported = Column(Boolean, nullable=False, default=False)
    low = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    fats = relationship("FaT")


class Mode(Base):
    __tablename__ = 'mode'

    id = Column(Integer, primary_key=True)
    name = Column(String(8), unique=True, nullable=False)
    ident = Column(String(8), unique=True, nullable=False)
    indicator = Column(String(1), nullable=True)
    supported = Column(Boolean, nullable=False, default=False)


class FaT(Base):
    __tablename__ = 'fat'

    id = Column(Integer, primary_key=True)
    f_tx = Column(Float, nullable=False)
    f_rx = Column(Float, nullable=False)
    t_tx = Column(Float, nullable=True)
    t_rx = Column(Float, nullable=True)
    band_id = Column(Integer, ForeignKey('band.id'), nullable=False)


class Token(Base):
    __tablename__ = 'token'

    token = Column(String(32), primary_key=True)
    owner = Column(String(32), nullable=False)
    active = Column(Boolean, nullable=False, default=False)


rep_has_modes = Table(
    'rep_has_modes',
    Base.metadata,
    Column('rep_id', Integer, ForeignKey('repeater.id')),
    Column('mod_id', Integer, ForeignKey('mode.id'))
)

rep_has_fats = Table(
    'rep_has_fats',
    Base.metadata,
    Column('rep_id', Integer, ForeignKey('repeater.id')),
    Column('fat_id', Integer, ForeignKey('fat.id'))
)


class Repeater(Base):
    __tablename__ = 'repeater'

    id = Column(Integer, primary_key=True)
    call = Column(String(8), unique=True, nullable=False)
    country_id = Column(Integer, ForeignKey('country.id'), nullable=False)
    country = relationship('Country')

    modes = relationship("Mode", secondary=rep_has_modes)
    fats = relationship("FaT", secondary=rep_has_fats)


class Store(Base):
    __tablename__ = 'store'

    name = Column(String, unique=True, nullable=False, primary_key=True)
    value = Column(String, unique=False, nullable=False)


class TgGroup(Base):
    __tablename__ = 'tg_group'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, unique=False, nullable=True)

    members = relationship('Dmr', back_populates='tg_group')


class ChannelGroup(Base):
    __tablename__ = 'channel_group'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, unique=False, nullable=True)

    channels = relationship('Channel', back_populates='channel_group')


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    comment = Column(String, unique=False, nullable=True)
    is_digit = Column(Boolean, nullable=False, default=False)
    slot = Column(SmallInteger, nullable=False, default=1)

    fat_id = Column(Integer, ForeignKey('fat.id'), nullable=False)
    fat = relationship('FaT')

    group_id = Column(Integer, ForeignKey('channel_group.id'), nullable=False)
    channel_group = relationship('ChannelGroup')


class Dmr(Base):
    __tablename__ = 'dmr'

    id = Column(Integer, primary_key=True)
    name = Column(String(26), unique=False, nullable=True)
    call = Column(String(8), unique=False, nullable=False)
    is_tg = Column(Boolean, nullable=False, default=False)
    country_id = Column(Integer, ForeignKey('country.id'), nullable=False)
    country = relationship('Country')
    description = Column(String, unique=False, nullable=True)
    tg_group_id = Column(Integer, ForeignKey('tg_group.id'), nullable=False)
    tg_group = relationship('TgGroup')
