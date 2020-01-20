__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from Base import *


class AuZipCodeArea(Base):

    __tablename__ = 'au_zipcode_area'

    id = Column(Integer, primary_key=True)
    code = Column(String, primary_key=True)
    description = Column(String)
    area_m2 = Column(Float)
    geometry = Column(Geometry('MULTIPOLYGON', 4326))

