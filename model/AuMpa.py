__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Float, Integer
from geoalchemy2 import Geometry
from Base import *


class AuMpa(Base):

    __tablename__ = 'au_mpa'

    id = Column(Integer, primary_key=True)
    spa_name = Column(String, )
    place_name = Column(String)
    spa_type = Column(String, )
    spa_type_name = Column(String)
    landuse = Column(Integer)
    area_m2 = Column(Float)
    geometry = Column(Geometry('POLYGON', 4326))