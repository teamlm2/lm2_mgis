__author__ = 'ankhbold'

from sqlalchemy import Column, String, Integer
from Base import *


class ClRcParcelType(Base):

    __tablename__ = 'cl_rc_parcel_type'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    id_column = Column(String)
    table_name = Column(String)
    python_model_name = Column(String)
    php_model_name = Column(String)
