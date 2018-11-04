__author__ = 'anna'
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from Base import *


class CtApplicationPersonRole(Base):

    __tablename__ = 'ct_application_person_role'

    application = Column(Integer, ForeignKey('ct_application.app_id'), primary_key=True)
    person = Column(Integer, ForeignKey('bs_person.person_id'), primary_key=True)
    role = Column(Integer, ForeignKey('cl_person_role.code'), primary_key=True)
    main_applicant = Column(Boolean)
    share = Column(Numeric(1, 2))
    app_no = Column(String)
    person_register = Column(String)

    person_ref = relationship("BsPerson", backref="ct_application_person_role", cascade="save-update")
    role_ref = relationship("ClPersonRole")