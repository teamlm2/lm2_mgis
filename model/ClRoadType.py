__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Float
from Base import *


class ClRoadType(Base):

    __tablename__ = 'cl_road_type'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)
    max_value = Column(Float)
    min_value = Column(Float)

