__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from Base import *
from ClAddressSource import *
from ClStreetType import *
from ClStreetShape import *

class StStreetAu2(Base):

    __tablename__ = 'st_street_au2'

    created_by = Column(Integer)
    created_at = Column(DateTime)


    street_id = Column(Integer, ForeignKey('st_street.id'), primary_key=True)
    street_id_ref = relationship("StStreet")

    au2 = Column(String, ForeignKey('au_level2.code'), primary_key=True)
    au2_ref = relationship("AuLevel2")
