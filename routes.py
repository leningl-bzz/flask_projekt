from flask import request, jsonify
from app import app, db
from models import Book


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
            "/books/update-fields/<id>": "PATCH to partially update a book by ID"
        }
    })


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

    title = data.get('title')
    author = data.get('author')
    genre = data.get('genre')
    year = data.get('year')

    if title and author:
        new_book = Book(title=title, author=author, genre=genre, year=year)
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"message": "Book added successfully"}), 201
    return jsonify({"error": "Title and author are required"}), 400


@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book_to_delete = Book.query.get_or_404(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"})


@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get_or_404(id)
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


@app.route('/books/author/<string:author>', methods=['GET'])
def get_books_by_author(author):
    books = Book.query.filter_by(author=author).all()
    return jsonify([{"id": book.id, "title": book.title, "genre": book.genre, "year": book.year} for book in books])


@app.route('/books/year-range', methods=['GET'])
def get_books_by_year_range():
    start_year = request.args.get('start', type=int)
    end_year = request.args.get('end', type=int)
    books = Book.query.filter(Book.year.between(start_year, end_year)).all()
    return jsonify([{"id": book.id, "title": book.title, "author": book.author, "genre": book.genre} for book in books])


@app.route('/books/update-fields/<int:id>', methods=['PATCH'])
def partial_update_book(id):
    book = Book.query.get_or_404(id)
    data = request.get_json()
    if 'title' in data: book.title = data['title']
    if 'author' in data: book.author = data['author']
    if 'genre' in data: book.genre = data['genre']
    if 'year' in data: book.year = data['year']
    db.session.commit()
    return jsonify({"message": "Book fields updated successfully"})
