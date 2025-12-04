from typing import Optional
from pony.orm import db_session
from werkzeug.security import generate_password_hash, check_password_hash
from ..repositories.user_repo import UserRepository
from ..exceptions import ValidationError, NotFoundError


class UserService:
    """Business logic for working with users."""

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    @db_session
    def register(self, email: str, name: str, password: str) -> dict:
        if not email or not name or not password:
            raise ValidationError("email, name and password are required")

        password_hash = generate_password_hash(password)
        user = self.repo.create(email=email, name=name, password_hash=password_hash)
        return user.to_dict()

    @db_session
    def authenticate(self, email: str, password: str) -> Optional[dict]:
        user = self.repo.get_by_email(email=email)
        if user is None:
            return None

        if not check_password_hash(user.password_hash, password):
            return None

        return user.to_dict()

    @db_session
    def get_user(self, user_id: int) -> dict:
        user = self.repo.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user.to_dict()
