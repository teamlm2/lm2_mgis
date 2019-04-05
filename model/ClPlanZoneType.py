__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Boolean, DateTime
from Base import *


class ClPlanZoneType(Base):

    __tablename__ = 'cl_plan_zone_type'

    plan_zone_type_id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    sort_order = Column(Integer)

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
