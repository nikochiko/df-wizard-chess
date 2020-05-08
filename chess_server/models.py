from chess_server import db


class UserModel(db.Model):
    # IDEA: Add a DateTime field to better manage multiple games by same user
    session_id = db.Column(db.String(36), primary_key=True)
    fen = db.Column(db.String(92), nullable=False)
    color = db.Column(db.Boolean, nullable=False)
