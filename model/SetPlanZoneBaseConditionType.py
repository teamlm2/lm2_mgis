__author__ = 'B.Ankhbold'

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from Base import *

class SetPlanZoneBaseConditionType(Base):

    __tablename__ = 'set_plan_zone_base_condition_type'

    plan_zone_id = Column(Integer, ForeignKey('cl_plan_zone.plan_zone_id'), primary_key=True)
    plan_zone_ref = relationship("ClPlanZone")

    base_condition_type_id = Column(Integer, ForeignKey('cl_base_condition_type.base_condition_type_id'), primary_key=True)
    base_condition_type_ref = relationship("ClBaseConditionType")
