__author__ = 'B.Ankhbold'

from sqlalchemy import Date, ForeignKey, Float, String, Integer
from sqlalchemy.orm import relationship
from LdProcessPlan import *

class SetProcessTypeColor(Base):

    __tablename__ = 'set_process_type_color'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    fill_color = Column(String)
    boundary_width = Column(Float)
    boundary_color = Column(String)
