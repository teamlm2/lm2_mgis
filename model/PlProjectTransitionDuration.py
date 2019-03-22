__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClZoneActivity import *

class PlProjectTransitionDuration(Base):

    __tablename__ = 'pl_project_transition_duration'

    id = Column(Integer, primary_key=True)
    description = Column(String)
    duration = Column(Integer)

    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)


    # foreign keys:
    project_id = Column(Integer, ForeignKey('pl_project.project_id'))
    project_ref = relationship("PlProject")

    transition_id = Column(Integer, ForeignKey('set_workrule_transition.workrule_transition_id'))
    transition_ref = relationship("SetWorkflowTransition")
