__author__ = 'anna'

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import relationship
from CtDecision import *
from CtDocument import *


class CtDecisionDocument(Base):

    __tablename__ = 'ct_decision_document'

    decision = Column(Integer, ForeignKey("ct_decision.decision_id"), primary_key=True)
    decision_ref = relationship("CtDecision")
    decision_no = Column(String)

    document = Column(Integer, ForeignKey("ct_document.id"), primary_key=True)
    document_ref = relationship("CtDocument")

