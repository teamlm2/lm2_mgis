__author__ = 'mwagner'

from sqlalchemy import Boolean, ForeignKey, Column, String, Integer
from Base import *


class CtApp1Ext(Base):

    __tablename__ = 'ct_app1_ext'

    app_id = Column(String, ForeignKey('ct_application.app_id'), primary_key=True)
    excess_area = Column(Integer)
    price_to_be_paid = Column(Integer)
    applicant_has_paid = Column(Boolean)

