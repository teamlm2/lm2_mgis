__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class CtContractDocument(Base):

    __tablename__ = 'ct_contract_document'

    contract = Column(Integer, ForeignKey('ct_contract.contract_id'), primary_key=True)
    contract_no = Column(String)

    document = Column(Integer, ForeignKey('ct_document.id'), primary_key=True)
    document_ref = relationship("CtDocument", backref="records", cascade="all")

    role = Column(Integer, ForeignKey('cl_document_role.code'))
    role_ref = relationship('ClDocumentRole')