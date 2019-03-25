__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class ClApplicationType(Base):

    __tablename__ = 'cl_application_type'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)
