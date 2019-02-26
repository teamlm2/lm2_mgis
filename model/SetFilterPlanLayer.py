__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Numeric, Integer, Sequence, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class SetFilterPlanLayer(Base):

    __tablename__ = 'set_filter_plan_layer'

    user_id = Column(Integer, ForeignKey('sd_user.user_id'), primary_key=True)
    user_ref = relationship("SdUser")

    process_type = Column(Integer, ForeignKey('ld_process_plan.code'), primary_key=True)
    process_ref = relationship("LdProcessPlan")

    plan_type = Column(Integer, ForeignKey('cl_plan_type.code'), primary_key=True)
    plan_type_ref = relationship("ClPlanType")

    au2 = Column(String, ForeignKey('au_level2.code'), primary_key=True)
    au2_ref = relationship("AuLevel2")
