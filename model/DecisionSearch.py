__author__ = 'anna'

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *
from ClApplicationType import *
from ClApplicationStatus import *
from SetRole import *


class DecisionSearch(Base):

    __tablename__ = 'decision_search'

    decision_id = Column(Integer, primary_key=True)
    decision_no = Column(String)
    decision_date = Column(Date)
    person_id = Column(Integer)
    person_register = Column(String)
    name = Column(String)
    first_name = Column(String)
    middle_name = Column(String)
    parcel_id = Column(String)
    app_no = Column(String)
    contract_no = Column(String)
    record_no = Column(String)