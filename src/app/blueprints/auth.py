from flask import Blueprint, request, jsonify
from ..repositories.user_repo import UserRepository
from ..services.user_service import UserService
from ..exceptions import ValidationError

auth_bp = Blueprint("auth", __name__)

_user_repo = UserRepository()
_user_service = UserService(_user_repo)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.get_json() or {}
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    if not email or not name or not password:
        raise ValidationError("email, name and password are required")

    user = _user_service.register(email=email, name=name, password=password)
    user.pop("password_hash", None)
    return jsonify(user), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Simple login endpoint returning a dummy token for demo purposes."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise ValidationError("email and password are required")

    user = _user_service.authenticate(email=email, password=password)
    if user is None:
        return jsonify({"error": {"type": "AuthenticationError", "message": "invalid credentials"}}), 401

    user_id = user["id"]
    token = f"demo-token-user-{user_id}"

    return jsonify(
        {
            "user": {"id": user_id, "email": user["email"], "name": user["name"]},
            "token": token,
        }
    )
