__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey
from Base import *


class CtContractCondition(Base):

    __tablename__ = 'ct_contract_conditions'

    contract_id = Column(Integer, ForeignKey('ct_contract.contract_id'), primary_key=True)
    condition_id = Column(Integer, ForeignKey('cl_contract_condition.code'), primary_key=True)
    sort_order = Column(Integer)
    # contract_no = Column(String)