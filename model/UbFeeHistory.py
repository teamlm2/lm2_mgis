__author__ = 'B.Ankhbold'

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Numeric, Integer, Sequence, ForeignKey, Float, Boolean, String, Date
from Base import *

class UbFeeHistory(Base):

    __tablename__ = 'ub_fee_history'

    id = Column(Integer, primary_key=True)
    person_register = Column(String)
    pid = Column(String)
    contract_no = Column(String)
    document_area = Column(Numeric)
    zoriulalt = Column(String)
    ner = Column(String)

    payment_contract = Column(Numeric)
    payment_before_less = Column(Numeric)
    payment_before_over = Column(Numeric)
    payment_year = Column(Numeric)
    payment_fund = Column(Numeric)
    payment_loss = Column(Numeric)
    payment_total = Column(Numeric)

    paid_before_less = Column(Numeric)
    paid_year = Column(Numeric)
    paid_fund = Column(Numeric)
    paid_city = Column(Numeric)
    paid_district = Column(Numeric)
    invalid_payment = Column(Numeric)
    paid_less = Column(Numeric)
    paid_over = Column(Numeric)

    description = Column(String)
    decision = Column(String)
    current_year = Column(Integer)

