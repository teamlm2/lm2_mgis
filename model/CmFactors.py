__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from Base import *

class CmFactors(Base):

    __tablename__ = 'cm_factors'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)

    factor_gruop = Column(Integer, ForeignKey('cm_factors_group.code'))
    factor_gruop_ref = relationship("CmFactorGroup")