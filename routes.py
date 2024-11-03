"""
Book API

Eine einfache RESTful API zur Verwaltung einer Bücherdatenbank mit Flask und SQLAlchemy.
Unterstützt CRUD-Operationen sowie flexible Filter- und Sortiermöglichkeiten.
"""

from flask import request, jsonify
from app import app, db
from models import Book
from functools import reduce


@app.route('/')
def index():
    """
    Endpoint to show available routes in the API.
    Returns:
        JSON response with a welcome message and a list of all available routes.
    """
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
    """
    Validates if required fields are present in the data.
    Args:
        required_fields (list): List of required fields.
    Returns:
        function: Validator function that checks if all required fields are present in the data.
    """

    def validator(data):
        return all(field in data for field in required_fields)

    return validator


validate_book_data = validate_data(["title", "author"])


@app.route('/books', methods=['GET'])
def get_books():
    """
    Endpoint to retrieve all books from the database.
    Returns:
        JSON response containing a list of all books.
    """
    books = Book.query.all()
    return jsonify(
        [{"id": book.id, "title": book.title, "author": book.author, "genre": book.genre, "year": book.year} for book in
         books]
    )


@app.route('/books', methods=['POST'])
def add_book():
    """
    Endpoint to add a new book to the database.
    Returns:
        JSON response with a success message if the book is added or an error message if data is invalid.
    """
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
    """
    Endpoint to delete a book by its ID.
    Returns:
        JSON response with a success message if the book is deleted or an error if the book is not found.
    """
    book_to_delete = Book.query.get_or_404(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"})


@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    """
    Endpoint to update a book's information by its ID.
    Returns:
        JSON response with a success message if the book is updated or an error if the book is not found.
    """
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
    """
    Endpoint to retrieve a specific book by its ID.
    Returns:
        JSON response containing the book information or an error if the book is not found.
    """
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
    """
    Filters books by the specified author.
    Args:
        author (str): Author name to filter books by.
    Returns:
        list: List of books by the specified author.
    """
    return Book.query.filter_by(author=author).all()


@app.route('/books/year-range', methods=['GET'])
def get_books_by_year_range():
    """
    Endpoint to retrieve books within a specified year range.
    Returns:
        JSON response containing a list of books within the specified year range.
    """
    start_year = request.args.get('start', type=int)
    end_year = request.args.get('end', type=int)
    books = Book.query.filter(Book.year.between(start_year, end_year)).all()
    books = sorted(books, key=lambda x: x.year)
    return jsonify([{"id": book.id, "title": book.title, "author": book.author, "genre": book.genre} for book in books])


@app.route('/books/earliest', methods=['GET'])
def get_earliest_book():
    """
    Endpoint to retrieve the earliest book by year.
    Returns:
        JSON response with the earliest book or an error if no books are found.
    """
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
    """
    Endpoint to partially update fields of a book by ID.
    Returns:
        JSON response with a success message if the book is updated or an error if the book is not found.
    """
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
    """
    Endpoint to get a summary of books published after 1800.
    Returns:
        JSON response with uppercase titles and total count of books published after 1800.
    """
    books = Book.query.all()
    recent_books = list(filter(lambda book: book.year > 1800, books))
    uppercase_titles = list(map(lambda book: book.title.upper(), recent_books))
    book_count = reduce(lambda acc, _: acc + 1, recent_books, 0)
    return jsonify({"titles": uppercase_titles, "book_count": book_count})


@app.route('/books/summary/<string:author>', methods=['GET'])
def get_books_summary_author(author):
    """
    Endpoint to get a summary of books by a specific author.
    Args:
        author (str): Author name to filter books by.
    Returns:
        JSON response with uppercase titles and total count of books by the specified author.
    """
    books = Book.query.all()
    filtered_books = books if author.lower() == "all" else list(filter(lambda book: book.author == author, books))
    transformed_titles = list(map(lambda book: book.title.upper(), filtered_books))
    total_books = reduce(lambda acc, _: acc + 1, filtered_books, 0)
    return jsonify({"titles": transformed_titles, "total_books": total_books})


@app.route('/books/uppercase', methods=['GET'])
def get_books_uppercase():
    """
    Endpoint to get all book titles in uppercase.
    Returns:
        JSON response with a list of uppercase book titles.
    """
    books = Book.query.all()
    titles_uppercase = list(map(lambda book: book.title.upper(), books))
    return jsonify(titles_uppercase)


@app.route('/books/count', methods=['GET'])
def get_books_count():
    """
    Endpoint to get the total count of books.
    Returns:
        JSON response with the total count of books.
    """
    books = Book.query.all()
    total_books = reduce(lambda acc, _: acc + 1, books, 0)
    return jsonify({"total_books": total_books})


@app.route('/books/sorted', methods=['GET'])
def get_books_sorted():
    """
    Endpoint to get books sorted by year in descending order.
    Returns:
        JSON response containing a list of books sorted by year in descending order.
    """
    books = Book.query.all()
    sorted_books = sorted(books, key=lambda book: book.year, reverse=True)
    return jsonify([{"title": book.title, "year": book.year} for book in sorted_books])


@app.route('/books/info', methods=['GET'])
def get_books_info():
    """
    Endpoint to get book information with title and year.
    Returns:
        JSON response with formatted title and year for each book.
    """
    books = Book.query.all()
    books_info = [{"info": (lambda title, year: f"{title} ({year})")(book.title, book.year)} for book in books]
    return jsonify(books_info)


@app.route('/books/capitalized', methods=['GET'])
def get_books_capitalized():
    """
    Endpoint to get all book titles in uppercase along with the year.
    Returns:
        JSON response with uppercase titles and year for each book.
    """
    books = Book.query.all()
    books_capitalized = [{"title": (lambda title: title.upper())(book.title), "year": book.year} for book in books]
    return jsonify(books_capitalized)


def create_filter(criteria):
    """
    Creates a filter function based on dynamic criteria.
    Args:
        criteria (dict): Dictionary with filter criteria (field and value).
    Returns:
        function: Filter function to apply on books.
    """

    def filter_books(book):
        return getattr(book, criteria["field"]) == criteria["value"]

    return filter_books


@app.route('/books/filter', methods=['GET'])
def filter_books_endpoint():
    """
    Endpoint to filter books by dynamic criteria (e.g., author).
    Returns:
        JSON response with filtered books based on criteria.
    """
    criteria = {"field": "author", "value": "Theodor Storm"}
    filter_func = create_filter(criteria)
    books = Book.query.all()
    filtered_books = [book for book in books if filter_func(book)]
    return jsonify([{"id": book.id, "title": book.title, "author": book.author} for book in filtered_books])


def apply_filter(data, filter_func):
    """
    Applies a filter function to the data.
    Args:
        data: Data to be filtered.
        filter_func: Function to filter data.
    Returns:
        Filtered data.
    """
    return filter_func(data)


def filter_books_by_author_lambda(author):
    """
    Filters books by author using a lambda function.
    Args:
        author (str): Author name to filter books by.
    Returns:
        list: List of books by the specified author.
    """
    return Book.query.filter_by(author=author).all()


def sort_books_by_year(books):
    """
    Sorts books by year.
    Args:
        books (list): List of books to be sorted.
    Returns:
        list: List of books sorted by year.
    """
    return sorted(books, key=lambda x: x.year)


@app.route('/books/author/<string:author>/sorted', methods=['GET'])
def get_sorted_books_by_author(author):
    """
    Endpoint to get books by a specific author sorted by year.
    Args:
        author (str): Author name to filter and sort books by.
    Returns:
        JSON response containing a list of books by the specified author, sorted by year.
    """
    books = filter_books_by_author(author)
    sorted_books = sort_books_by_year(books)
    return jsonify([{"id": book.id, "title": book.title, "year": book.year} for book in sorted_books])
