from pydantic import BaseModel, Field
from typing import Literal

class EmailTriageResult(BaseModel):
    category: Literal["urgent", "follow_up", "archive"] = Field(description="Classify the email into one of these three buckets.")
    
    urgency_score: int = Field(description="Score from 1 to 5, where 5 is critically urgent and 1 is noise.", ge=1, le=5)
    
    draft_reply: str = Field(description="If category is 'urgent', provide a two-sentence contextual draft reply. Otherwise, return an empty string.")