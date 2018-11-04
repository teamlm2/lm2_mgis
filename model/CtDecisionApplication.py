__author__ = 'anna'

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import relationship
from ClDecision import *
from ClDecisionLevel import *
from CtDecision import *
from CtApplication import *


class CtDecisionApplication(Base):

    __tablename__ = 'ct_decision_application'

    application = Column(Integer, ForeignKey('ct_application.app_id'), primary_key=True)
    application_ref = relationship("CtApplication")
    app_no = Column(String)

    decision = Column(Integer, ForeignKey("ct_decision.decision_id"))
    decision_ref = relationship("CtDecision")
    decision_no = Column(String)

    decision_result = Column(Integer, ForeignKey("cl_decision.code"))
    decision_result_ref = relationship("ClDecision")