__author__ = 'anna'

from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from Base import *
from SetRole import *


class CtApplicationStatus(Base):

    __tablename__ = 'ct_application_status'

    status_date = Column(Date)

    application = Column(Integer, ForeignKey('ct_application.app_id'), primary_key=True)
    #application_ref = relationship("CtApplication")

    status = Column(Integer, ForeignKey('cl_application_status.code'), primary_key=True)
    status_ref = relationship("ClApplicationStatus")

    officer_in_charge = Column(Integer, ForeignKey('sd_user.user_id'))
    officer_in_charge_ref = relationship("SdUser", foreign_keys=[officer_in_charge], cascade="save-update")

    next_officer_in_charge = Column(Integer, ForeignKey('sd_user.user_id'))
    next_officer_in_charge_ref = relationship("SdUser", foreign_keys=[next_officer_in_charge], cascade="save-update")
