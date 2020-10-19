__author__ = 'ankhbold'

from sqlalchemy import Column, String, Integer, Boolean
from Base import *

class ClLanduseMovementStatus(Base):

    __tablename__ = 'cl_landuse_movement_status'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)
    is_confirm = Column(Boolean)
    is_draft = Column(Boolean)
