__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Numeric, Integer, Sequence, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class SetFilterPlanLayer(Base):

    __tablename__ = 'set_filter_plan_layer'

    user_id = Column(Integer, ForeignKey('sd_user.user_id'), primary_key=True)
    user_ref = relationship("SdUser")

    badedturl = Column(Integer, ForeignKey('ld_process_plan.code'))
    process_ref = relationship("LdProcessPlan")

    plan_type = Column(Integer, ForeignKey('cl_plan_type.code'))
    plan_type_ref = relationship("ClPlanType")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")
