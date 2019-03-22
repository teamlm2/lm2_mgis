__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClZoneActivity import *

class SetPlanTypeWorkrule(Base):

    __tablename__ = 'set_plan_type_workrile'

    created_at = Column(DateTime)
    created_by = Column(Integer)

    # foreign keys:
    plan_type_id = Column(Integer, ForeignKey('cl_plan_type.plan_type_id'), primary_key=True)
    plan_type_ref = relationship("ClPlanType")

    workrule_id = Column(Integer, ForeignKey('set_workrule.workrule_id'), primary_key=True)
    workrule_ref = relationship("SetWorkrule")

