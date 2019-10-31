__author__ = 'B.Ankhbold'

from sqlalchemy import Date, DateTime, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from CtFee import *
from CtContractCondition import *


class CtContract(Base):

    __tablename__ = 'ct_contract'

    contract_id = Column(Integer, primary_key=True)
    contract_no = Column(String)
    contract_date = Column(Date)
    contract_begin = Column(Date)
    contract_end = Column(Date)
    certificate_no = Column(Integer)
    cancellation_date = Column(Date)
    property_no = Column(String)
    type = Column(Integer)

    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # foreign keys:
    status = Column(Integer, ForeignKey('cl_contract_status.code'))
    status_ref = relationship("ClContractStatus")

    cancellation_reason = Column(Integer, ForeignKey('cl_contract_cancellation_reason.code'))
    cancellation_reason_ref = relationship("ClContractCancellationReason")

    application_roles = relationship("CtContractApplicationRole", backref="contract_ref",
                                     lazy='dynamic', cascade="all, delete-orphan")
    documents = relationship("CtContractDocument", backref="contract_ref",
                             lazy='dynamic', cascade="all, delete-orphan")

    fees = relationship("CtFee", backref='contract_ref', lazy='dynamic', cascade="all, delete, delete-orphan")
    archived_fees = relationship("CtArchivedFee", backref='contract_ref',
                                 lazy='dynamic', cascade="all, delete, delete-orphan")

    conditions = relationship("CtContractCondition", backref="contract_ref",
                              lazy='dynamic', cascade="all, delete, delete-orphan")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")