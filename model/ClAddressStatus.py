__author__ = 'ankhbold'

from sqlalchemy import Column, String, Integer, Boolean
from Base import *

class ClAddressStatus(Base):

    __tablename__ = 'cl_address_status'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)
