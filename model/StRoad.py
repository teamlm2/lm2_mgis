__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from Base import *
from ClAddressSource import *
from ClStreetType import *
from ClRoadType import *

class StRoad(Base):

    __tablename__ = 'st_road'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_en = Column(String)
    description = Column(String)
    is_active = Column(Boolean)
    valid_from = Column(Date)
    valid_till = Column(Date)
    area_m2 = Column(Float)
    length = Column(Float)
    geometry = Column(Geometry('POLYGON', 4326))
    line_geom = Column(Geometry('LINESTRING', 4326))

    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    road_type_id = Column(Integer, ForeignKey('cl_road_type.code'))
    road_type_id_ref = relationship("ClRoadType")

    street_id = Column(Integer, ForeignKey('st_street.id'))
    street_id_ref = relationship("StStreet")

    in_source = Column(Integer, ForeignKey('cl_address_source.code'))
    in_source_ref = relationship("ClAddressSource")

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    au3 = Column(String, ForeignKey('au_level3.code'))
    au3_ref = relationship("AuLevel3")