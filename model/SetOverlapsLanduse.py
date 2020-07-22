__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from Base import *

class SetOverlapsLanduse(Base):
    __tablename__ = 'set_overlaps_landuse'

    in_landuse = Column(Integer, ForeignKey('cl_landuse_type.code'), primary_key=True)
    # in_landuse_ref = relationship("ClLanduseType")

    ch_landuse = Column(String, ForeignKey('cl_landuse_type.code'), primary_key=True)
    # ch_landuse_ref = relationship("ClLanduseType")

    is_input_landuse = Column(Boolean)