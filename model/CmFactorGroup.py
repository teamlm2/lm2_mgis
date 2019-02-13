__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from Base import *

class CmFactorGroup(Base):

    __tablename__ = 'cm_factors_group'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)