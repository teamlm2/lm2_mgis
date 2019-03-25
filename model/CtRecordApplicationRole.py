__author__ = 'B.Ankhbold'

from sqlalchemy import ForeignKey, Column, String, Integer
from sqlalchemy.orm import relationship
from Base import *
from CtContract import *
from CtApplication import *
from ClApplicationRole import *


class CtRecordApplicationRole(Base):

    __tablename__ = 'ct_record_application_role'

    record = Column(Integer, ForeignKey('ct_ownership_record.record_id'), primary_key=True)
    record_no = Column(String)
    app_no = Column(String)
    application = Column(Integer, ForeignKey('ct_application.app_id'), primary_key=True)
    application_ref = relationship("CtApplication")

    role = Column(Integer, ForeignKey('cl_application_role.code'))
    #role_ref = relationship("ClApplicationRole")
