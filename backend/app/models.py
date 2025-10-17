"""
SQLAlchemy ORM models.

This module defines the database schema for providers and plans.  Providers
represent retail electric providers (REPs) such as Reliant, Gexa, TXU and
Direct Energy.  Plans represent individual electricity plans offered by
providers, including pricing tiers and additional features.
"""
from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Provider(Base):
    __tablename__ = "providers"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, unique=True, nullable=False)
    website: str = Column(String, nullable=True)

    plans = relationship("Plan", back_populates="provider")

    def __repr__(self) -> str:
        return f"Provider(id={self.id}, name={self.name})"


class Plan(Base):
    __tablename__ = "plans"

    id: int = Column(Integer, primary_key=True, index=True)
    provider_id: int = Column(Integer, ForeignKey("providers.id"), nullable=False)
    plan_name: str = Column(String, nullable=False)
    plan_url: str = Column(String, nullable=True)  # Direct link to plan on provider website
    plan_type: str = Column(String, nullable=True)
    service_type: str = Column(String, nullable=True, default="Residential")  # Residential or Commercial
    zip_code: str = Column(String, nullable=True)  # Zip code where plan is available
    contract_months: int = Column(Integer, nullable=True)
    rate_500_cents: float = Column(Float, nullable=True)
    rate_1000_cents: float = Column(Float, nullable=True)
    rate_2000_cents: float = Column(Float, nullable=True)
    monthly_bill_1000: float = Column(Float, nullable=True)
    monthly_bill_2000: float = Column(Float, nullable=True)
    early_termination_fee: float = Column(Float, nullable=True)
    base_monthly_fee: float = Column(Float, nullable=True)
    renewable_percent: int = Column(Integer, nullable=True)
    special_features: str = Column(String, nullable=True)
    last_updated: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    provider = relationship("Provider", back_populates="plans")

    def __repr__(self) -> str:
        return f"Plan(id={self.id}, provider_id={self.provider_id}, plan_name={self.plan_name})"