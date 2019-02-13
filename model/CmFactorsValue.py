__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Numeric
from Base import *


class CmFactorsValue(Base):

    __tablename__ = 'cm_factors_value'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    value = Column(Numeric)