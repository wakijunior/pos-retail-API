from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User   # adjust import if needed

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()

        user = User.query.filter_by(email=current_user).first()

        if not user or user.role != "admin":
            return jsonify({"msg": "Admins only"}), 403

        return fn(*args, **kwargs)

    return wrapper