__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from Base import *

class CmFactor(Base):

    __tablename__ = 'cm_factor'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    name_en = Column(String)
    is_active = Column(Boolean)
    factor_data_type = Column(String)
    description = Column(String)
    is_fraction = Column(Boolean)
    is_calculated = Column(Boolean)
    is_auto_calculated = Column(Boolean)

    landuse_type = Column(Integer, ForeignKey('cm_cama_landuse.code'))
    landuse_type_ref = relationship("CmCamaLanduseType")