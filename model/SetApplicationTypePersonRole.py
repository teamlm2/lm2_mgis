__author__ = 'B.Ankhbold'

from sqlalchemy import Column, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from Base import *


class SetApplicationTypePersonRole(Base):

    __tablename__ = 'set_application_type_person_role'

    type = Column(Integer, ForeignKey('cl_application_type.code'), primary_key=True)
    type_ref = relationship("ClApplicationType")

    role = Column(Integer, ForeignKey('cl_person_role.code'), primary_key=True)
    role_ref = relationship("ClPersonRole")

    is_required = Column(Boolean)
    is_owner = Column(Boolean)
