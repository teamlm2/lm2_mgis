__author__ = 'anna'

from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from Base import *
from ClApplicationType import *
from ClApplicationStatus import *
from SetRole import *


class ContractSearch(Base):

    __tablename__ = 'contract_search'

    contract_id = Column(Integer, primary_key=True)
    contract_no = Column(String)
    certificate_no = Column(Integer)
    status = Column(Integer)
    person_role = Column(Integer)
    contract_date = Column(Date)
    person_id = Column(Integer)
    person_register = Column(String)
    name = Column(String)
    first_name = Column(String)
    middle_name = Column(String)
    parcel_id = Column(String)
    app_no = Column(String)
    decision_no = Column(String)
    au2_code = Column(String)
    app_type = Column(Integer)