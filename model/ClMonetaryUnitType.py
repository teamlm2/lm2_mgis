__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class ClMonetaryUnitType(Base):

    __tablename__ = 'cl_monetary_unit_type'

    code = Column(Integer, primary_key=True)
    short_name = Column(String)
    description = Column(String)
