__author__ = 'b.ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class ClEntryType(Base):

    __tablename__ = 'cl_entry_type'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)
    color = Column(String)
