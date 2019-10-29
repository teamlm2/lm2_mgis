__author__ = 'B.Ankhbold'

from sqlalchemy import Date, ForeignKey, Column, Integer, String, Numeric, DateTime
from sqlalchemy.orm import relationship
from CtFee import *
from ClDecisionLevel import *
from CtDecisionApplication import *
from CtDecisionDocument import *

from CtDocument import *

class PaPaymentPaid(Base):

    __tablename__ = 'pa_payment_paid'

    id = Column(Integer, primary_key=True)
    paid_year = Column(Integer)
    remainning_amount = Column(Numeric)
    earning_amount = Column(Numeric)
    quarter_one = Column(Numeric)
    quarter_two = Column(Numeric)
    quarter_three = Column(Numeric)
    quarter_four = Column(Numeric)
    total_amount = Column(Numeric)
    invalid_amount = Column(Numeric)
    year_amount = Column(Numeric)

    imposition_year_amount = Column(Numeric)
    imposition_total_amount = Column(Numeric)
    contract_amount = Column(Numeric)

    status_id = Column(Integer)
    created_by = Column(Integer)
    updated_by = Column(Integer)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # other foreign keys:
    fee_id = Column(Integer, ForeignKey('ct_fee.id'))
    fee_ref = relationship("CtFee")

    imposition_id = Column(Integer)

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    parcel_id = Column(String, ForeignKey('ca_parcel_tbl.parcel_id'))
    contract_id = Column(Integer, ForeignKey('ct_contract.contract_id'))
    person_id = Column(Integer, ForeignKey('bs_person.person_id'))
    type_id = Column(Integer)