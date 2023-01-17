from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship

# declarative base class
Base = declarative_base()

# an example mapping using the base
class Participant(Base):
    __tablename__ = "participant"

    contactId = Column(String, primary_key=True)
    email = Column(String)
    phone_number = Column(String)

class Distribution(Base):
    __tablename__ = "distributions"

    id = Column(String, primary_key=True)
    expirationDate = Column(Date)
    mailistListId = Column(String)
    distributionList = relationship('DistributionList')
    surveyId = Column(String)

class DistributionList(Base):
    __tablename__ = "distribution_list"

    id = Column(Integer, primary_key=True)
    surveyLink = Column(String)
    surveyStatus = Column(String)
    surveyDelivered = Column(Boolean)
    linkExpiration = Column(Date)
    distributionId = Column(String, ForeignKey('distributions.id'))
    participantId = Column(String, ForeignKey('participant.contactId'))
