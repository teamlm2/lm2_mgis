__author__ = 'ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class ClPersonGroupType(Base):

    __tablename__ = 'cl_person_group_type'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)
