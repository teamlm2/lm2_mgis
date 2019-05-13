__author__ = 'B.Ankhbold'
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from Base import *

class PlSetRightFormRightType(Base):

    __tablename__ = 'set_right_form_right_type'

    right_form_id = Column(Integer, ForeignKey('pl_project_parcel.right_form_id'), primary_key=True)
    right_type_code = Column(Integer, ForeignKey('cl_right_type.code'), primary_key=True)
