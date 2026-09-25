from pydantic import BaseModel
from typing import List


class CompactAnswer(BaseModel):
    answer: str
    facts: List[str]
    source_chunks: List[int]