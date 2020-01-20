__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class ClAddressSource(Base):

    __tablename__ = 'cl_address_source'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)
    source_type = Column(String)
