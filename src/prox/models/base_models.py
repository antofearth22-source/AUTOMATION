from datetime import date
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, validator
import uuid

# Define literal types for validation
Gender = Literal["Male", "Female", "Other"]
BerthPreference = Literal["Lower", "Middle", "Upper", "Side Lower", "Side Upper", "Window Side", "No Preference"]
FoodPreference = Literal["Veg", "Non-Veg", "No Food"]
TrainClassCode = Literal["SL", "1A", "2A", "3A", "3E", "CC", "EC", "2S"]
QuotaCode = Literal["GN", "TQ", "PT", "LD"]
BrowserType = Literal["chrome", "edge", "brave"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]

class IRCTCAccount(BaseModel):
    """Represents the credentials for an IRCTC account."""
    label: str = Field(..., min_length=1, description="A user-friendly nickname for the account.")
    username: str = Field(..., min_length=1, description="The IRCTC username.")
    password: str = Field(..., min_length=1, description="The IRCTC password. Stored as plain text in this version.")

class Passenger(BaseModel):
    """Represents a single passenger for a booking."""
    name: str = Field(..., min_length=1)
    age: int = Field(..., gt=0, lt=126)
    gender: Gender = "Male"
    berth_preference: BerthPreference = "No Preference"
    food_preference: FoodPreference = "No Food"

class Journey(BaseModel):
    """Represents the travel details for a ticket."""
    from_station: str = Field(..., min_length=1)
    to_station: str = Field(..., min_length=1)
    train_no: Optional[str] = None
    train_name: Optional[str] = None
    class_code: TrainClassCode = "SL"
    quota: QuotaCode = "GN"
    journey_date: date

    @validator("to_station")
    def stations_must_be_different(cls, v, values):
        if 'from_station' in values and v == values['from_station']:
            raise ValueError("From and To stations cannot be the same.")
        return v

class TicketTemplate(BaseModel):
    """Represents a complete, reusable booking template."""
    template_id: str = Field(default_factory=lambda: f"tkt_{uuid.uuid4().hex[:12]}")
    label: str = Field(..., min_length=1, description="A user-friendly name for this template.")
    irctc_username: str = Field(..., min_length=1, description="The IRCTC account to use for this booking.")
    journey: Journey
    passengers: List[Passenger] = Field(..., min_items=1, max_items=6)
    mobile: str = Field(..., regex=r"^[6-9]\d{9}$")
    email: Optional[str] = None
    payment_mode_label: Optional[str] = None

class Settings(BaseModel):
    """Represents the application's user-configurable settings."""
    preferred_browser: BrowserType = "chrome"
    chrome_path: Optional[str] = None
    edge_path: Optional[str] = None
    brave_path: Optional[str] = None
    time_offset_seconds_before_tatkal: int = 10
    log_level: LogLevel = "INFO"
    truecaptcha_api_key: Optional[str] = None
    truecaptcha_user_id: Optional[str] = None
