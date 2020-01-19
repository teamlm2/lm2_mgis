__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from Base import *
from ClAddressSource import *
from ClStreetType import *

class StStreet(Base):

    __tablename__ = 'st_street'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_mn = Column(String)
    description = Column(String)
    is_active = Column(Boolean)
    valid_from = Column(Date)
    valid_till = Column(Date)
    area_m2 = Column(Float)
    geometry = Column(Geometry('MULTIPOLYGON', 4326))
    line_geom = Column(Geometry('MULTILINESTRING', 4326))

    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    street_type_id = Column(Integer, ForeignKey('cl_street_type.code'))
    street_type_id_ref = relationship("ClStreetType")

    in_source = Column(Integer, ForeignKey('cl_address_source.code'))
    in_source_ref = relationship("ClAddressSource")