__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class PsRcParcelValue(Base):

    __tablename__ = 'ps_rc_parcel_value'

    gid = Column(String)
    rc_id = Column(String, ForeignKey('ps_recovery_class.id'), primary_key=True)
    rc_ref = relationship("PsRecoveryClass")

    parcel_type = Column(Integer, ForeignKey('cl_rc_parcel_type.code'), primary_key=True)
    parcel_type_ref = relationship("ClRcParcelType")

    monitoring_year = Column(Integer)