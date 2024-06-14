from init import db, ma

class User(db.Model):
    # Name of the table
    __tablename__ = "users"

    # Attributes of the table
    id = db.Column(db.Intger, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class UserSchema(ma.Schema):
    class Meta:
        fileds = ( "id", "name", "email", "password", "is_admin" )


# To handle a single user object
user_schema = UserSchema(exclude=["password"])
# To handle a list of user objects
users_schema = UserSchema(many=True, exclude=["password"])