__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from ClPlanZone import *

class PlProjectPlanZone(Base):

    __tablename__ = 'pl_project_plan_zone'

    created_at = Column(DateTime)
    created_by = Column(Integer)

    # foreign keys:

    project_id = Column(Integer, ForeignKey('pl_project.project_id'), primary_key=True)
    project_ref = relationship("PlProject")

    plan_zone_id = Column(Integer, ForeignKey('cl_plan_zone.plan_zone_id'), primary_key=True)
    plan_zone_ref = relationship("ClPlanZone")


