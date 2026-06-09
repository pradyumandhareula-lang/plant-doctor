from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class PlantDiagnostic(Base):
    __tablename__ = "diagnostics"

    id = Column(Integer, primary_key=True, index=True)
    plant_name = Column(String, index=True, default="Unknown Plant")
    condition_summary = Column(String, default="Analyzing...")
    detailed_report = Column(Text)
    image_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
