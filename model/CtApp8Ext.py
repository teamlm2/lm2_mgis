__author__ = 'B.Ankhbold'

from sqlalchemy import Date, ForeignKey, Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from ClMortgageType import *


class CtApp8Ext(Base):

    __tablename__ = 'ct_app8_ext'

    id = Column(Integer, primary_key=True)
    app_id = Column(String, ForeignKey('ct_application.app_id'))
    start_mortgage_period = Column(Date)
    end_mortgage_period = Column(Date)
    app_no = Column(String)
    monetary_unit_value = Column(Numeric)
    mortgage_contract_no = Column(String)
    loan_contract_no = Column(String)

    # other foreign keys:
    mortgage_type = Column(Integer, ForeignKey('cl_mortgage_type.code'))
    mortgage_type_ref = relationship("ClMortgageType")

    mortgage_status = Column(Integer, ForeignKey('cl_mortgage_status.code'))
    mortgage_status_ref = relationship("ClMortgageStatus")

    person_id = Column(Integer, ForeignKey('bs_person.person_id'))
    person_ref = relationship("BsPerson")

    monetary_unit_type = Column(Integer, ForeignKey('cl_monetary_unit_type.code'))
    monetary_unit_type_ref = relationship("ClMonetaryUnitType")
