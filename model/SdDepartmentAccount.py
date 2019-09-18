__author__ = 'B.Ankhbold'
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from Base import *

class SdDepartmentAccount(Base):

    __tablename__ = 'hr_department_account'

    department_id = Column(String, ForeignKey('hr_department.department_id'), primary_key=True)
    department_ref = relationship("SdDepartment")

    bank_id = Column(Integer, ForeignKey('cl_bank.code'), primary_key=True)
    bank_ref = relationship("ClBank")

    account_no = Column(String, primary_key=True)