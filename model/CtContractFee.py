__author__ = 'B.Ankhbold'

from sqlalchemy import ForeignKey, Column, String, Integer, Numeric, DateTime
from Base import *
from sqlalchemy.orm import relationship
from CtFeePayment import *
from CtFineForFeePayment import *
from ClPaymentFrequency import *

class CtContractFee(Base):

    __tablename__ = 'ct_contract_fee'

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('ct_contract.contract_id'))
    level_id = Column(Integer)
    base_price_m2 = Column(Numeric)
    zone_id = Column(Integer, ForeignKey('set_fee_zone.zone_id'))
    confidence_percent = Column(Numeric)
    subsidized_area = Column(Integer)
    subsidized_fee_rate = Column(Numeric)
    base_fee_per_m2 = Column(Numeric)
    area = Column(Numeric)
    landuse_area = Column(Numeric)
    zone_area = Column(Numeric)
    amount = Column(Numeric)
    base_fee_id = Column(Integer)
    resolution_id = Column(Integer)

    created_by = Column(Integer)
    created_at = Column(DateTime)