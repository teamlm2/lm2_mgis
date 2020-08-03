__author__ = 'ankhbold'

from sqlalchemy import Column, String, Integer, Boolean
from Base import *

class ClParcelType(Base):

    __tablename__ = 'cl_parcel_type'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    table_name = Column(String)
    python_model_name = Column(String)
    php_model_name = Column(String)
    layer_type = Column(Integer)
    is_insert_state_parcel = Column(Boolean)
