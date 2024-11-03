from flask import request, jsonify
from app import app, db
from models import Book
from functools import reduce


@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to the Book API!",
        "routes": {
            "/books": "GET all books",
            "/books": "POST a new book",
            "/books/<id>": "DELETE a book by ID",
            "/books/<id>": "PUT to update a book by ID",
            "/books/author/<author>": "GET books by a specific author",
            "/books/year-range?start=<start_year>&end=<end_year>": "GET books within a specific year range",
            "/books/update-fields/<id>": "PATCH to partially update a book by ID",
            "/books/earliest": "GET the earliest book by year"
        }
    })


def validate_data(required_fields):
    def validator(data):
        return all(field in data for field in required_fields)

    return validator


validate_book_data = validate_data(["title", "author"])


@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify(
        [{"id": book.id, "title": book.title, "author": book.author, "genre": book.genre, "year": book.year} for book in
         books])


@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "No JSON data provided"}), 400
    if not validate_book_data(data):
        return jsonify({"error": "Title and author are required"}), 400
    new_book = Book(title=data['title'], author=data['author'], genre=data.get('genre'), year=data.get('year'))
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully"}), 201


@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book_to_delete = Book.query.get_or_404(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"})


@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({"error": f"No book found with id {id}"}), 404
    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.genre = data.get('genre', book.genre)
    book.year = data.get('year', book.year)
    db.session.commit()
    return jsonify({"message": "Book updated successfully"})


@app.route('/books/<int:id>', methods=['GET'])
def get_book_by_id(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({"error": f"No book found with id {id}"}), 404
    return jsonify({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "year": book.year
    })


# Functional example - filter for author
def filter_books_by_author(author):
    return Book.query.filter_by(author=author).all()


@app.route('/books/author/<string:author>', methods=['GET'])
def get_books_by_author(author):
    books = filter_books_by_author(author)
    return jsonify([{"id": book.id, "title": book.title, "genre": book.genre, "year": book.year} for book in books])


@app.route('/books/year-range', methods=['GET'])
def get_books_by_year_range():
    start_year = request.args.get('start', type=int)
    end_year = request.args.get('end', type=int)
    books = Book.query.filter(Book.year.between(start_year, end_year)).all()
    books = sorted(books, key=lambda x: x.year)
    return jsonify([{"id": book.id, "title": book.title, "author": book.author, "genre": book.genre} for book in books])


@app.route('/books/earliest', methods=['GET'])
def get_earliest_book():
    books = Book.query.all()
    if not books:
        return jsonify({"error": "No books found"}), 404
    earliest_book = reduce(lambda a, b: a if a.year < b.year else b, books)
    return jsonify({
        "id": earliest_book.id,
        "title": earliest_book.title,
        "author": earliest_book.author,
        "genre": earliest_book.genre,
        "year": earliest_book.year
    })


@app.route('/books/update-fields/<int:id>', methods=['PATCH'])
def patch_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({"error": f"No book found with id {id}"}), 404
    data = request.get_json()
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'genre' in data:
        book.genre = data['genre']
    if 'year' in data:
        book.year = data['year']
    db.session.commit()
    return jsonify({"message": "Book updated successfully"})
