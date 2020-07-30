from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from Base import *


class AuDispute(Base):

    __tablename__ = 'au_dispute'

    id = Column(String, primary_key=True)
    description = Column(String)
    area_m2 = Column(Float)
    geometry = Column(Geometry('POLYGON', 4326))
    au2 = Column(String)
