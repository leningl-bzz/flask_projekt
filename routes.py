from functools import reduce
from flask import request, jsonify
from app import app, db
from models import Book


# B4G, B4F, B4E: Map, Filter und Reduce zur Verarbeitung der Bücherliste, C1G: Klarheit durch sprechende
# Variablennamen und klare Struktur
def validate_and_process_books(books, required_fields=None):
    """Validiert und verarbeitet die Bücherliste."""
    if required_fields is None:
        required_fields = ["title", "author"]

    # B4G: Filter für Jahr und erforderliche Felder, A1G: Pure function zur Filterung, C1F: Filter für gültige Bücher
    valid_books = filter(lambda book: all(field in book for field in required_fields) and book.get("year", 0) > 1800,
                         books)

    # B4G: Map für Grossbuchstaben-Titel, A1F: Transformation der Titel in Grossbuchstaben, C1F: Titel in Grossbuchstaben umwandeln
    processed_books = map(lambda book: {**book, "title": book["title"].upper()}, valid_books)

    # B4G, B4F, B4E: Reduce für komplexe Datenverarbeitung (Zählen, Summieren),
    # A1E: Aggregation von Daten mit funktionalem Ansatz, B3F: Lambda mit zwei Argumenten in reduce, C1E: Zusammenfassen der Daten
    aggregated_data = reduce(lambda acc, book: {
        "count": acc["count"] + 1,
        "total_years": acc["total_years"] + book["year"],
        "books": acc["books"] + [book]
    }, processed_books, {"count": 0, "total_years": 0, "books": []})

    # B4E: Durchschnittsjahr aus Aggregation
    average_year = aggregated_data["total_years"] / aggregated_data["count"] if aggregated_data["count"] > 0 else 0
    return {"processed_books": aggregated_data["books"], "book_count": aggregated_data["count"],
            "average_year": average_year}


# B1G, B1F, B1E: Funktionale Programmierung für Buchzusammenfassungen
def get_books_summary(books):
    """Erstellt eine Zusammenfassung der Bücherliste."""
    # B4G: Filter für Bücher nach Jahr
    filtered_books = filter(lambda book: book["year"] > 1800, books)  # B3G: Einfache Lambda für Jahr-Filterung

    # B4G, B4F: Map für Titel in Grossbuchstaben
    transformed_books = list(map(lambda book: {**book, "title": book["title"].upper()}, filtered_books))

    count = len(transformed_books)

    return {"titles_uppercase": list(transformed_books), "book_count": count}


# B3E: Lambda für Sortieren nach Jahr
def sort_books_by_year(books):
    """Sortiert die Bücherliste nach Erscheinungsjahr."""
    return sorted(books, key=lambda book: book["year"])


# C1G, C1F, C1E: Refactoring und Code-Optimierung für die Buch-API
def filter_books(books, min_year=1800, required_fields=None):
    """Filtert Bücher nach Mindestjahr und erforderlichen Feldern."""
    if required_fields is None:
        required_fields = ["title", "author"]
    return filter(lambda book: all(field in book for field in required_fields) and book.get("year", 0) > min_year,
                  books)


# B2G, B2F, B2E: Funktionen als Objekte und Argumente, sowie Verwendung von Closures
def to_uppercase(book):
    """Transformiert den Buchtitel in Grossbuchstaben."""
    return {**book, "title": book["title"].upper()}


def to_lowercase(book):
    """Transformiert den Buchtitel in Kleinbuchstaben."""
    return {**book, "title": book["title"].lower()}


# B2G: Liste mit Transformationen
transformations = [to_uppercase, to_lowercase]


# B2F: Funktion nimmt Transformationsfunktionen an
def apply_transformations(books, transform_funcs):
    """Wendet Transformationen auf die Bücherliste an."""
    for func in transform_funcs:
        books = map(func, books)
    return books


# B3E, B2E: Closure für Jahr-Filter
def create_year_filter(min_year):
    """Erstellt einen Jahr-Filter als Closure."""
    return lambda book: book["year"] >= min_year  # Closure, das eine spezifische Filterfunktion zurückgibt


# API-Endpunkte
@app.route('/')
def index():
    """Begrüssungsnachricht der Book API."""
    return jsonify({
        "message": "Willkommen zur Book API!",
        "routes": {
            "/books/process-data": "POST zum Validieren und Verarbeiten der Buecherliste",
            "/books/summary": "GET Zusammenfassung der Buecher, die nach 1800 veroeffentlicht wurden",
            "/books/sorted": "GET Buecher nach Erscheinungsjahr sortiert",
            "/books/add": "POST - Neues Buch hinzufuegen"
        }
    })


@app.route('/books/process-data', methods=['POST'])
def process_books_data_endpoint():
    """API-Endpunkt zur Verarbeitung der Bücherliste."""
    data = request.get_json()
    books = data.get("books", [])
    result = validate_and_process_books(books)
    return jsonify(result)


@app.route('/books/summary', methods=['GET'])
def get_books_summary_endpoint():
    """API-Endpunkt für die Buchzusammenfassung."""
    books = Book.query.all()
    book_dicts = [{"title": book.title, "author": book.author, "year": book.year} for book in books]
    summary = get_books_summary(book_dicts)
    return jsonify(summary)


@app.route('/books/sorted', methods=['GET'])
def sort_books_by_year_endpoint():
    """API-Endpunkt zum Sortieren der Bücher nach Jahr."""
    books = Book.query.all()
    book_dicts = [{"title": book.title, "author": book.author, "year": book.year} for book in books]
    sorted_books = sort_books_by_year(book_dicts)
    return jsonify(sorted_books)


@app.route('/books/add', methods=['POST'])
def add_book():
    """Fügt ein neues Buch zur Datenbank hinzu."""
    data = request.get_json()
    new_book = Book(title=data["title"], author=data["author"], year=data.get("year", 0), genre=data.get("genre", ""))
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Buch erfolgreich hinzugefügt!"}), 201
