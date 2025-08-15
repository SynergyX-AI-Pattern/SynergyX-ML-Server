from pydantic import BaseModel
from typing import Optional

class ImageSearchResponse(BaseModel):
    id: Optional[int]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1
            }
        }
    }