from typing import Optional
from pydantic import Field, BaseModel

class CommonNameCandidate(BaseModel):
    common_name: str = Field(
        description="The common name of the coral species"
    )
    confidence_score: float = Field(
        description="The confidence score of the common name"
    )

class DCA_Agent_State(BaseModel):
    input_filename: str = Field(
        description="The filename of the coral species data to be processed."
    )
    output_filename: str = Field(
        default="",
        description="The filename of the coral species data to be processed."
    )
    common_name_candidates: list[CommonNameCandidate] = Field(
        default_factory=list,
        description="A list of potential common names for the coral species"
    )
    selected_species_id: Optional[str] = Field(
        default=None,
        description="The 7-character species identifier (Common Abbre) selected from the codebook"
    )
    date: Optional[str] = Field(
        default=None,
        description="Datetime that corresponds to the record. "
    )