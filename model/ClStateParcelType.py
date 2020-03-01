__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *

class ClStateParcelType(Base):

    __tablename__ = 'cl_state_parcel_type'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)