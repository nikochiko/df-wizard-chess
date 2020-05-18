from chess_server import db


class UserModel(db.Model):
    # IDEA: Add a DateTime field to better manage multiple games by same user
    session_id = db.Column(db.String(128), primary_key=True)
    board = db.Column(db.PickleType, nullable=False)
    color = db.Column(db.Boolean, nullable=False)
