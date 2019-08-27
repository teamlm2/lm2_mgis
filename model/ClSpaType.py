__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class ClSpaType(Base):

    __tablename__ = 'cl_spa_type'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    short_name = Column(String)
    description_en = Column(String)
