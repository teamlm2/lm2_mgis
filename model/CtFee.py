__author__ = 'mwagner'

from sqlalchemy import ForeignKey, Column, String, Integer, Numeric
from Base import *
from sqlalchemy.orm import relationship
from CtFeePayment import *
from CtFineForFeePayment import *
from ClPaymentFrequency import *


class CtFee(Base):

    __tablename__ = 'ct_fee'

    id = Column(Integer, primary_key=True)
    contract = Column(Integer, ForeignKey('ct_contract.contract_id'))
    person = Column(Integer, ForeignKey('bs_person.person_id'))
    share = Column(Numeric)
    area = Column(Integer)
    fee_calculated = Column(Integer)
    fee_contract = Column(Integer)
    grace_period = Column(Integer)
    base_fee_per_m2 = Column(Integer)
    subsidized_area = Column(Integer)
    subsidized_fee_rate = Column(Numeric)
    contract_no = Column(String)
    person_register = Column(String)

    base_fee_id = Column(Integer, ForeignKey('set_base_fee.id'))
    base_fee_ref = relationship("SetBaseFee")
    # foreign keys:
    payment_frequency = Column(Integer, ForeignKey('cl_payment_frequency.code'))
    payment_frequency_ref = relationship("ClPaymentFrequency")

    payments = relationship("CtFeePayment", backref='fee_ref', lazy='dynamic', cascade="all, delete, delete-orphan")
    fine_payments = relationship("CtFineForFeePayment", backref='fee_ref', lazy='dynamic', cascade="all, delete, delete-orphan")