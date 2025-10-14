"""
Pydantic schema definitions for serialization and validation.

The API returns instances of these schemas to the client.  They define
which fields are exposed in responses and which fields are accepted in
requests.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PlanBase(BaseModel):
    plan_name: str
    plan_type: Optional[str] = None
    service_type: Optional[str] = "Residential"
    zip_code: Optional[str] = None
    contract_months: Optional[int] = None
    rate_500_cents: Optional[float] = None
    rate_1000_cents: Optional[float] = None
    rate_2000_cents: Optional[float] = None
    monthly_bill_1000: Optional[float] = None
    monthly_bill_2000: Optional[float] = None
    early_termination_fee: Optional[float] = None
    base_monthly_fee: Optional[float] = None
    renewable_percent: Optional[int] = None
    special_features: Optional[str] = None


class PlanCreate(PlanBase):
    provider_id: int


class Plan(PlanBase):
    id: int
    provider_id: int
    last_updated: datetime

    class Config:
        from_attributes = True


class ProviderBase(BaseModel):
    name: str
    website: Optional[str] = None


class ProviderCreate(ProviderBase):
    pass


class Provider(ProviderBase):
    id: int
    plans: List[Plan] = []

    class Config:
        from_attributes = True