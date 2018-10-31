__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Date, Boolean, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from ClEmployeeType import *
from ClUserCancelReason import *
from Base import *


class SdUser(Base):

    __tablename__ = 'sd_user'

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    photo = Column(String)
    remember_token = Column(String)
    created_at = Column(Date)
    updated_at = Column(Date)
    deleted_at = Column(Date)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    last_active = Column(Date)

    gis_user_real = Column(Integer, ForeignKey('set_role.user_name_real'))
    gis_user_real_ref = relationship("SetRole")