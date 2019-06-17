__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from LdProcessPlan import *

class ClAttributeZoneGroup(Base):

    __tablename__ = 'ld_attribute_group'

    id = Column(Integer, primary_key=True)
    group_name = Column(String)
    description = Column(String)

