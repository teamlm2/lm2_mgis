__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *
from ClApplicationStatus import *
from ClApplicationType import *
from SetRole import *


class MaintenanceSearch(Base):

    __tablename__ = 'maintenance_search'

    gid = Column(Integer, primary_key=True)
    id = Column(Integer)
    completion_date = Column(Date)
    case_id = Column(String)

    created_by = Column(String, ForeignKey('set_role_user.user_name'))
    completed_by = Column(String, ForeignKey('set_role_user.user_name'))

    parcel = Column(String)
    building = Column(String)
    app_no = Column(String)
    soum = Column(String)

    surveyed_by_land_office = Column(String)
    surveyed_by_surveyor = Column(String)

    company = Column(String)

    person_id = Column(String)
    person_register = Column(String)
    name = Column(String)
    first_name = Column(String)