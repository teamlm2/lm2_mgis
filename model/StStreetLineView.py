__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from Base import *
from ClAddressSource import *
from ClStreetType import *

class StStreetLineView(Base):

    __tablename__ = 'st_street_line_view'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    decision_date = Column(Date)
    decision_no = Column(String)
    description = Column(String)
    is_active = Column(Boolean)
    geometry = Column(Geometry('MULTILINESTRING', 4326))

    decision_level_id = Column(Integer, ForeignKey('cl_plan_decision_level.plan_decision_level_id'))
    decision_level_id_ref = relationship("ClPlanDecisionLevel")

    street_type_id = Column(Integer, ForeignKey('cl_street_type.code'))
    street_type_id_ref = relationship("ClStreetType")

