__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class CmCamaLanduseType(Base):

    __tablename__ = 'cm_cama_landuse'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)

    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")