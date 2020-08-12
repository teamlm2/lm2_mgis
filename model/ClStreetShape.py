__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class ClStreetShape(Base):

    __tablename__ = 'cl_street_shape'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)

