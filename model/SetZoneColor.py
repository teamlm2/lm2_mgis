__author__ = 'B.Ankhbold'

from sqlalchemy import Date, ForeignKey, Float, String, Integer, Column
from sqlalchemy.orm import relationship
from ClZoneActivity import *

class SetZoneColor(Base):

    __tablename__ = 'set_zone_color'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    fill_color = Column(String)
    boundary_width = Column(Float)
    boundary_color = Column(String)
