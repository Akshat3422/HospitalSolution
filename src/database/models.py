from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text
)
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PatientEncounter(Base):
    __tablename__ = "patient_encounters"

    id = Column(Integer, primary_key=True)

    subject_id = Column(BigInteger)
    hadm_id = Column(BigInteger)

    admission_type = Column(String(50))
    admission_location = Column(String(100))
    discharge_location = Column(String(100))
    insurance = Column(String(50))
    marital_status = Column(String(50))
    race = Column(String(100))
    gender = Column(String(10))

    anchor_age = Column(Integer)

    drug = Column(String(150))
    formulary_drug_cd = Column(String(100))
    prod_strength = Column(String(150))
    dose_val_rx = Column(String(100))
    dose_unit_rx = Column(String(50))
    form_unit_disp = Column(String(50))
    route = Column(String(50))
    clinical_embeddings = Column(Vector(768))
    clinical_text = Column(Text)
    # description = Column(Text)

    eventtype = Column(String(50))
    careunit = Column(String(100))
    order_type = Column(String(50))
    order_subtype = Column(String(50))
    transaction_type = Column(String(50))

    spec_type_desc = Column(String(150))
    test_name = Column(String(150))
    org_name = Column(String(150))
    ab_name = Column(String(150))

    comments = Column(Text)

    drg_type = Column(String(50))
    description = Column(Text)
    drg_severity = Column(String(50))
    drg_mortality = Column(String(50))