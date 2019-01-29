__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Boolean
from Base import *


class ClPlanType(Base):

    __tablename__ = 'cl_plan_type'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)
    is_point = Column(Boolean)
    short_name = Column(String)
