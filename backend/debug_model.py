from models import User
from sqlmodel import SQLModel
# Compatibility for older pydantic/sqlmodel versions
try:
    fields = User.model_fields
except AttributeError:
    fields = User.__fields__

print(f"User id field type: {fields['id'].annotation}")
print(f"User id field default: {fields['id'].default}")

from sqlalchemy.schema import CreateTable
from sqlalchemy import create_engine
engine = create_engine("sqlite:///:memory:")
print("DDL for User:")
print(CreateTable(User.__table__).compile(engine))
