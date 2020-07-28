__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, ForeignKey,Sequence
from sqlalchemy.orm import relationship, backref
from Base import *
from StStreetPoint import *
from StStreet import *

class StMapStreetPoint(Base):

    __tablename__ = 'st_map_street_point'

    id = Column(Integer, primary_key=True)

    street_point_id = Column(String, ForeignKey('st_street_point.id'))
    street_point_id_ref = relationship("StStreetPoint")

    street_id = Column(Integer, ForeignKey('st_street.id'))
    street_id_ref = relationship("StStreet")

