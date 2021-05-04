from . import constants
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.types import TypeDecorator, CHAR

db = SQLAlchemy()


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'sqlite':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Audit(db.Model):
    id = db.Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    user_id = db.Column(GUID, db.ForeignKey("users.id"), nullable=False)
    action_performed = db.Column(db.Enum(
        constants.ENCRYPTED_SECRET,
        constants.DECRYPTED_SECRET,
        constants.MODIFIED_SECRET,
    ), nullable=False)
    inputs = db.Column(JSON)

    def __repr__(self):
        return '<Audit %r>' % self.id


class Secrets(db.Model):
    id = db.Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    encrypted_value = db.Column(db.BLOB, nullable=False)

    @property
    def as_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "value": str(self.encrypted_value),
        }

    def __repr__(self):
        return '<Secrets %r>' % self.name


class Users(db.Model):
    id = db.Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    key_id = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id


class UsersSecrets(db.Model):
    id = db.Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    key_id = db.Column(db.String(80), db.ForeignKey("users.key_id"), nullable=False)
    secret_id = db.Column(GUID, db.ForeignKey("secrets.id"), nullable=False)

    def __repr__(self):
        return '<UsersSecrets %r>' % self.id
