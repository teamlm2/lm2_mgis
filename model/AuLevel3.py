__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Float, ForeignKey
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from Base import *


class AuLevel3(Base):

    __tablename__ = 'au_level3'

    code = Column(String, primary_key=True)
    name = Column(String)
    area_m2 = Column(Float)
    geometry = Column(Geometry('POLYGON', 4326))

    au2_code = Column(String, ForeignKey('au_level2.code'))
    au2_code_ref = relationship("AuLevel2")