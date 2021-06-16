
__author__ = 'B.Ankhbold'
from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *

class SetCheckPlanTypeCadastre(Base):

    __tablename__ = 'set_check_plan_type_cadastre'

    is_active = Column(Boolean)
    created_at = Column(Date)
    updated_at = Column(Date)
    created_by = Column(Integer)
    updated_by = Column(Integer)


    # foreign keys:
    plan_type_id = Column(Integer, ForeignKey('cl_plan_type.plan_type_id'),  primary_key=True)
    plan_type_id_ref = relationship("ClPlanType")

    right_form_id = Column(String, ForeignKey('cl_right_form.right_form_id'),  primary_key=True)
    right_form_id_ref = relationship("ClRightForm")