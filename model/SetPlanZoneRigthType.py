__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClPlanZone import *

class SetPlanZoneRigthType(Base):

    __tablename__ = 'set_plan_zone_right_type'

    # foreign keys:
    right_type_code = Column(Integer, ForeignKey('cl_right_type.code'), primary_key=True)
    right_type_ref = relationship("ClRightType")

    plan_zone_id = Column(Integer, ForeignKey('cl_plan_zone.plan_zone_id'), primary_key=True)
    plan_zone_ref = relationship("ClPlanZone")


