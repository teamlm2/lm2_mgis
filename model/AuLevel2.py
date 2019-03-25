__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from Base import *


class AuLevel2(Base):

    __tablename__ = 'au_level2'

    code = Column(String, primary_key=True)
    name = Column(String)
    area_m2 = Column(Float)
    geometry = Column(Geometry('POLYGON', 4326))

    au1_code = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")
