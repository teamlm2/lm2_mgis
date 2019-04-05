__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from Base import *


class PlProjectZoneMainSub(Base):

    __tablename__ = 'pl_project_zone_main_sub'

    zone_sub_id = Column(String, ForeignKey('cl_zone_sub.zone_sub_id'), primary_key=True)
    zone_sub_ref = relationship("ClZoneSub")

    plan_zone_id = Column(String, ForeignKey('cl_plan_zone.plan_zone_id'), primary_key=True)
    zone_main_ref = relationship("ClPlanZone")

    project_id = Column(Integer, ForeignKey('pl_project.project_id'), primary_key=True)
    project_ref = relationship("PlProject")

    created_at = Column(DateTime)
    created_by = Column(Integer)