__author__ = 'B.Ankhbold'

from sqlalchemy import String,Date, Integer, Column, Numeric, ForeignKey
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from ClZoneType import *
from SetBaseFee import *

class SetFeeZone(Base):

    __tablename__ = 'set_fee_zone'

    location = Column(String)
    zone_no = Column(Integer)
    area_m2 = Column(Numeric)
    valid_from = Column(Date)
    valid_till = Column(Date)
    zone_id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    fees = relationship("SetBaseFee", backref='parent', cascade="all, delete, delete-orphan")
    documents = relationship("SetFeeDocument", lazy="dynamic", cascade="all, delete-orphan")

    zone_type =  Column(Integer, ForeignKey('cl_zone_type.code'))
    zone_ref = relationship("ClZoneType")
