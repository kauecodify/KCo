from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class PartBase(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=160)
    category: str = "general"
    description: str = ""
    specifications: dict = {}
    dimensions: str = ""
    tolerances: str = ""
    approval_criteria: dict = {}
    active: bool = True


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    specifications: dict | None = None
    dimensions: str | None = None
    tolerances: str | None = None
    approval_criteria: dict | None = None
    active: bool | None = None


class PartImageOut(BaseModel):
    id: int
    path: str
    is_primary: bool

    class Config:
        from_attributes = True


class PartOut(PartBase):
    id: int
    version: int
    version_history: list = []
    created_at: datetime
    updated_at: datetime
    images: list[PartImageOut] = []

    class Config:
        from_attributes = True


class InspectionOut(BaseModel):
    id: str
    part_id: int | None
    part_code: str
    part_name: str
    image_path: str
    status: str
    confidence: float
    match_score: float
    divergences: list = []
    latency_ms: dict = {}
    operator: str
    device_info: str
    synced_offline: bool
    review_status: str
    reviewed_by: str
    review_note: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewRequest(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")
    note: str = ""


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(pattern="^(operator|supervisor|admin)$")
    full_name: str = ""
    plant: str = "MX-01"


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    full_name: str
    plant: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ModelVersionOut(BaseModel):
    id: int
    name: str
    version: str
    engine_type: str
    parameters: dict = {}
    active: bool
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True
