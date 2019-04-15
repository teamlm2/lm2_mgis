__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from LdProcessPlan import *

class LdAttribute(Base):

    __tablename__ = 'ld_attribute'

    id = Column(Integer, primary_key=True)
    attribute_name = Column(String)
    attribute_name_mn = Column(String)
    attribute_type = Column(String)
    description = Column(String)

    # foreign keys:
    attribute_group = Column(Integer, ForeignKey('ld_attribute_group.id'))
    attribute_group_ref = relationship("LdAttributeGroup")
