__author__ = 'B.Ankhbold'

from sqlalchemy import ForeignKey, Column, String, Integer, Numeric
from Base import *
from sqlalchemy.orm import relationship
from CtFeePayment import *
from CtFineForFeePayment import *
from ClPaymentFrequency import *


class CtContractPastureValue(Base):

    __tablename__ = 'ct_contract_pasture_value'

    contract = Column(Integer, ForeignKey('ct_contract.contract_id'), primary_key=True)
    parcel = Column(String, ForeignKey('ca_pasture_parcel_tbl.parcel_id'), primary_key=True)
    current_value = Column(Numeric)
    value_year = Column(Integer, primary_key=True)
    contract_no = Column(String)

    # foreign keys:
    pasture_value = Column(Integer, ForeignKey('cl_pasture_values.code'), primary_key=True)
    pasture_value_ref = relationship("ClPastureValues")
