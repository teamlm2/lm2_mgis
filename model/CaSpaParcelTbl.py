
__author__ = 'B.Ankhbold'
from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *
from ClSpaType import *
from ClSpaMood import *
from ClPlanDecisionLevel import *

class CaSpaParcelTbl(Base):

    __tablename__ = 'ca_spa_parcel_tbl'

    parcel_id = Column(String, primary_key=True)
    spa_land_name = Column(String)
    area_m2 = Column(Float)
    spa_law = Column(String)
    decision_date = Column(Date)
    decision_no = Column(String)
    contract_date = Column(Date)
    contract_no = Column(String)
    certificate_date = Column(Date)
    certificate_no = Column(String)
    person_register = Column(String)
    valid_from = Column(Date)
    valid_till = Column(Date)
    geometry = Column(Geometry('POLYGON', 4326))

    # foreign keys:
    spa_type = Column(Integer, ForeignKey('cl_spa_type.code'))
    spa_type_ref = relationship("ClSpaType")

    spa_mood = Column(Integer, ForeignKey('cl_spa_mood.code'))
    spa_mood_ref = relationship("ClSpaMood")

    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")

    decision_level = Column(Integer, ForeignKey('cl_plan_decision_level.code'))
    decision_level_ref = relationship("ClPlanDecisionLevel")

    department_id = Column(String, ForeignKey('hr_department.department_id'))
    department_ref = relationship("SdDepartment")

    #applications = relationship("CtApplication")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")