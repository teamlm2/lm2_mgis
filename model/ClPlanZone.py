__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from Base import *
from SetRole import *


class ClPlanZone(Base):

    __tablename__ = 'cl_plan_zone'

    plan_zone_id = Column(Integer,  primary_key=True)
    code = Column(String)
    name = Column(String)

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    plan_zone_type_id = Column(Integer, ForeignKey('cl_plan_zone_type.plan_zone_type_id'))