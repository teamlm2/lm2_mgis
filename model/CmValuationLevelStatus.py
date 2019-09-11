__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class CmValuationLevelStatus(Base):

    __tablename__ = 'cm_valuation_level_status'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)
