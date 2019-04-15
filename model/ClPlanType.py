__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Boolean, DateTime
from Base import *


class ClPlanType(Base):

    __tablename__ = 'cl_plan_type'

    plan_type_id = Column(Integer, primary_key=True)
    code = Column(String)
    description = Column(String)
    description_en = Column(String)
    is_point = Column(Boolean)
    short_name = Column(String)
    admin_unit_type = Column(Integer)

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
