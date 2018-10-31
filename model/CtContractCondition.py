__author__ = 'anna'

from sqlalchemy import Column, Integer, String, ForeignKey
from Base import *


class CtContractCondition(Base):

    __tablename__ = 'ct_contract_conditions'

    contract = Column(Integer, ForeignKey('ct_contract.contract_id'), primary_key=True)
    condition = Column(Integer, ForeignKey('cl_contract_condition.code'), primary_key=True)