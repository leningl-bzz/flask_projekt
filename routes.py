from flask import request, jsonify
from app import app, db
from models import Book
from functools import reduce


@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to the Book API!",
        "routes": {
            "/books": "GET all books, POST a new book",
            "/books/<id>": "DELETE a book by ID, PUT to update a book by ID",
            "/books/author/<author>": "GET books by a specific author using a flexible filter function",
            "/books/author/<author>/sorted": "GET books by a specific author, sorted by year",
            "/books/year-range?start=<start_year>&end=<end_year>": "GET books within a specific year range",
            "/books/update-fields/<id>": "PATCH to partially update a book by ID",
            "/books/earliest": "GET the earliest book by year",
            "/books/summary": "GET a summary of books published after 1800, using map, filter, and reduce",
            "/books/summary/<author>": "GET a summary of books by a specific author using map, filter, and reduce",
            "/books/sorted": "GET books sorted by year in descending order using a lambda expression",
            "/books/info": "GET book information with title and year using a lambda expression with multiple arguments",
            "/books/capitalized": "GET all book titles in uppercase using a simple lambda expression",
            "/books/filter": "GET books filtered by dynamic criteria using a closure",
            "/books/uppercase": "GET all book titles in uppercase using map",
            "/books/count": "GET the total count of books using reduce"
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


def filter_books_by_author(author):
    return Book.query.filter_by(author=author).all()


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


@app.route('/books/summary', methods=['GET'])
def get_books_summary():
    books = Book.query.all()
    recent_books = list(filter(lambda book: book.year > 1800, books))
    uppercase_titles = list(map(lambda book: book.title.upper(), recent_books))
    book_count = reduce(lambda acc, _: acc + 1, recent_books, 0)
    return jsonify({"titles": uppercase_titles, "book_count": book_count})


@app.route('/books/summary/<string:author>', methods=['GET'])
def get_books_summary_author(author):
    books = Book.query.all()
    filtered_books = books if author.lower() == "all" else list(filter(lambda book: book.author == author, books))
    transformed_titles = list(map(lambda book: book.title.upper(), filtered_books))
    total_books = reduce(lambda acc, _: acc + 1, filtered_books, 0)
    return jsonify({"titles": transformed_titles, "total_books": total_books})


@app.route('/books/uppercase', methods=['GET'])
def get_books_uppercase():
    books = Book.query.all()
    titles_uppercase = list(map(lambda book: book.title.upper(), books))
    return jsonify(titles_uppercase)


@app.route('/books/by-author/<string:author>', methods=['GET'])
def get_books_by_author_b4g(author):
    books = Book.query.all()
    books_by_author = list(filter(lambda book: book.author == author, books))
    return jsonify([{"title": book.title, "year": book.year} for book in books_by_author])


@app.route('/books/count', methods=['GET'])
def get_books_count():
    books = Book.query.all()
    total_books = reduce(lambda acc, _: acc + 1, books, 0)
    return jsonify({"total_books": total_books})


@app.route('/books/sorted', methods=['GET'])
def get_books_sorted():
    books = Book.query.all()
    sorted_books = sorted(books, key=lambda book: book.year, reverse=True)
    return jsonify([{"title": book.title, "year": book.year} for book in sorted_books])


@app.route('/books/info', methods=['GET'])
def get_books_info():
    books = Book.query.all()
    books_info = [{"info": (lambda title, year: f"{title} ({year})")(book.title, book.year)} for book in books]
    return jsonify(books_info)


@app.route('/books/capitalized', methods=['GET'])
def get_books_capitalized():
    books = Book.query.all()
    books_capitalized = [{"title": (lambda title: title.upper())(book.title), "year": book.year} for book in books]
    return jsonify(books_capitalized)


def create_filter(criteria):
    def filter_books(book):
        return getattr(book, criteria["field"]) == criteria["value"]

    return filter_books


@app.route('/books/filter', methods=['GET'])
def filter_books_endpoint():
    criteria = {"field": "author", "value": "Theodor Storm"}
    filter_func = create_filter(criteria)
    books = Book.query.all()
    filtered_books = [book for book in books if filter_func(book)]
    return jsonify([{"id": book.id, "title": book.title, "author": book.author} for book in filtered_books])


def apply_filter(data, filter_func):
    return filter_func(data)


def filter_books_by_author_lambda(author):
    return Book.query.filter_by(author=author).all()


@app.route('/books/author/<string:author>', methods=['GET'])
def get_books_by_author_combined(author):
    books = apply_filter(author, lambda auth: filter_books_by_author_lambda(auth))
    return jsonify(
        [{"id": book.id, "title": book.title, "genre": book.genre, "year": book.year, "author": book.author} for book in
         books])


def sort_books_by_year(books):
    return sorted(books, key=lambda x: x.year)


@app.route('/books/author/<string:author>/sorted', methods=['GET'])
def get_sorted_books_by_author(author):
    books = filter_books_by_author(author)
    sorted_books = sort_books_by_year(books)
    return jsonify([{"id": book.id, "title": book.title, "year": book.year} for book in sorted_books])
