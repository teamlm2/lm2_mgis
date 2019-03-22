__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClZoneActivity import *

class ClDocumentType(Base):

    __tablename__ = 'cl_attribute_group'

    document_type_id = Column(Integer, primary_key=True)
    code = Column(String)
    description = Column(String)
    description_en = Column(String)

    is_required = Column(Boolean)
    type = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
