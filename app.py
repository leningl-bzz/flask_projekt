"""
App-Konfiguration für die Book API

Initialisiert die Flask-Anwendung und die SQLAlchemy-Datenbank.
Konfiguriert die Datenbankverbindung und lädt alle Routen.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from routes import *

if __name__ == '__main__':
    app.run(debug=True)
