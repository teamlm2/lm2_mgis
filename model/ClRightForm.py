__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class ClRightForm(Base):

    __tablename__ = 'cl_right_form'

    right_form_id = Column(Integer, primary_key=True)
    code = Column(String)
    description = Column(String)
    description_en = Column(String)
