__author__ = 'mwagner'

from sqlalchemy import ForeignKey, Column, String, Integer
from sqlalchemy.orm import relationship
from Base import *
from CtContract import *
from CtApplication import *
from ClApplicationRole import *


class CtContractApplicationRole(Base):

    __tablename__ = 'ct_contract_application_role'

    contract = Column(Integer, ForeignKey('ct_contract.contract_id'), primary_key=True)

    application = Column(Integer, ForeignKey('ct_application.app_id'), primary_key=True)
    # application_ref = relationship("CtApplication")

    role = Column(Integer, ForeignKey('cl_application_role.code'))
    role_ref = relationship("ClApplicationRole")
