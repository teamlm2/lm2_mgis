__author__ = 'Ankhbold'

from sqlalchemy import Column, String, Integer, Date,DateTime, Boolean, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from ClEmployeeType import *
from ClUserCancelReason import *
from Base import *


class SdEmployee(Base):

    __tablename__ = 'hr_employee'

    employee_id = Column(Integer, primary_key=True)
    firstname = Column(String)
    lastname = Column(String)
    urag_name = Column(String)
    mobile_phone = Column(String)
    employee_type_id = Column(Integer)
    address_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    hired_date = Column(Date)
    terminated_date = Column(Date)
    is_active = Column(Integer)
    email = Column(String)
    register_number = Column(String)
    home_phone = Column(String)
    birth_aimag_city_id = Column(Integer)
    birth_soum_district_id = Column(Integer)
    is_married = Column(Integer)
    education_type_id = Column(Integer)
    profile_photo = Column(String)
    time_attendance_code = Column(String)

    department_id = Column(Integer, ForeignKey('hr_department.department_id'))
    department_ref = relationship("SdDepartment")

    position_id = Column(Integer, ForeignKey('hr_position.position_id'))
    position_ref = relationship("SdPosition")

    user_id = Column(Integer, ForeignKey('sd_user.user_id'))
    user_ref = relationship("SdUser")