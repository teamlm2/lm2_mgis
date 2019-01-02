__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from Base import *
from SetRole import *


class CtApplicationStatus(Base):

    __tablename__ = 'ct_application_status'
    app_status_id = Column(Integer,  primary_key=True)
    status_date = Column(DateTime)
    description = Column(String)
    application = Column(Integer, ForeignKey('ct_application.app_id'))
    app_no = Column(String)
    #application_ref = relationship("CtApplication")

    status = Column(Integer, ForeignKey('cl_application_status.code'))
    status_ref = relationship("ClApplicationStatus")

    officer_in_charge = Column(Integer, ForeignKey('sd_user.user_id'))
    officer_in_charge_ref = relationship("SdUser", foreign_keys=[officer_in_charge], cascade="save-update")

    next_officer_in_charge = Column(Integer, ForeignKey('sd_user.user_id'))
    next_officer_in_charge_ref = relationship("SdUser", foreign_keys=[next_officer_in_charge], cascade="save-update")
