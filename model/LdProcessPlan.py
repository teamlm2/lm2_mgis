__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from Base import *
from SetRole import *


class LdProcessPlan(Base):

    __tablename__ = 'ld_process_plan'

    code = Column(Integer,  primary_key=True)
    description = Column(String)
    description_en = Column(String)
    parent_code = Column(String)