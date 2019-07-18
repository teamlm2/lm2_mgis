__author__ = 'B.Ankhbold'

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from Base import *

class SetPlanZoneRelation(Base):

    __tablename__ = 'set_plan_zone_relation'

    parent_plan_zone_id = Column(Integer, ForeignKey('cl_plan_zone.plan_zone_id'), primary_key=True)
    # parent_plan_zone_ref = relationship("ClPlanZone")

    child_plan_zone_id = Column(Integer, ForeignKey('cl_plan_zone.plan_zone_id'), primary_key=True)
    # child_plan_zone_ref = relationship("ClPlanZone")
