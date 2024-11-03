"""
Datenmodell für Bücher

Definiert die Book-Klasse als SQLAlchemy-Modell für die Speicherung von Buchdaten.
Erstellt die Datenbanktabelle, wenn sie nicht existiert.
"""

from app import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=True)
    year = db.Column(db.Integer, nullable=True)


with db.app.app_context():
    db.create_all()
