from pydantic import BaseModel


class studentBase(BaseModel):
    # student_id is intentionally excluded here — the DB assigns it automatically via SERIAL.
    # Accepting it from the client would let users overwrite existing IDs.
    student_name: str
    age: int
    standard: int