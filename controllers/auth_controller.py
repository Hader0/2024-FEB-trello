from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import create_access_token
from datetime import timedelta

from init import bcrypt, db
from models.user import User, user_schema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register_user():
    try:
        # get the data from the body of the request
        body_data = request.get_json()
        # create an instance of the User model
        user = User(
            name=body_data.get("name"),
            email=body_data.get("email")
        )
        # extract the password from the body
        password = body_data.get("password")

        # hash the password
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")

        # add and commit to the DB
        db.session.add(user)
        db.session.commit()

        # respond back
        return user_schema.dump(user), 201

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            # Not null violation
            return {"error": f"The column {err.orig.diag.column_name} is required"}, 409
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Unique violation
            return {"error": "Email address already in use"}, 409
        
@auth_bp.route("/login", methods=["POST"])
def login_user():
    # Get the data from the body of the request
    body_data = request.get_json()
    # Find the user in the Databse with that email address
    stmt = db.select(User).filterby(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    # If user exists and password is correct
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # Create jwt
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        # Respond back
        return {"email": user.email, "is_admin": user.is_admin, "token": token}
    else:
        # Respond back with an error message
        return {"error": "Invalid email or password"}, 401