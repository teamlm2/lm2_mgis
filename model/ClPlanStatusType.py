__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class ClPlanStatusType(Base):

    __tablename__ = 'cl_plan_status_type'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)
