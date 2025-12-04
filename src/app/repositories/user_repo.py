from typing import Optional
from ..models import User
from ..exceptions import ValidationError


class UserRepository:
    """Persistence operations for User entity."""

    def create(self, email: str, name: str, password_hash: str) -> User:
        existing = User.get(email=email)
        if existing is not None:
            raise ValidationError("User with this email already exists")

        user = User(email=email, name=name, password_hash=password_hash)
        return user

    def get(self, user_id: int) -> Optional[User]:
        return User.get(id=user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return User.get(email=email)
