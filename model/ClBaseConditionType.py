__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from Base import *
from SetRole import *


class ClBaseConditionType(Base):

    __tablename__ = 'cl_base_condition_type'

    base_condition_type_id = Column(Integer,  primary_key=True)
    code = Column(String)
    short_name = Column(String)
    description = Column(String)
    description_en = Column(String)

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)