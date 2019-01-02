__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Float, Integer
from geoalchemy2 import Geometry
from Base import *


class AuMpaZone(Base):

    __tablename__ = 'au_mpa_zone'

    id = Column(Integer, primary_key=True)
    spa_name = Column(String, )
    place_name = Column(String)
    zone_type = Column(String, )
    zone_type_name = Column(String)
    landuse = Column(Integer)
    area_m2 = Column(Float)
    geometry = Column(Geometry('POLYGON', 4326))