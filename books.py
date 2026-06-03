from fastapi import FastAPI, Body  # FastAPI is the app framework; Body parses the request body as JSON

app = FastAPI()  # create the FastAPI application instance

# in-memory list of books acting as a temporary database
Books = [
    {'title': 'title1', 'author': 'author1', 'category': 'science'},
    {'title': 'title2', 'author': 'author2', 'category': 'science'},
    {'title': 'title3', 'author': 'author3', 'category': 'history'},
    {'title': 'title4', 'author': 'author4', 'category': 'math'},
    {'title': 'title5', 'author': 'author5', 'category': 'math'},
    {'title': 'title6', 'author': 'author2', 'category': 'math'}
]


@app.get("/books")  # GET /books — returns all books
def read_root():
    return Books


@app.get("/books/{book_author}")  # GET /books/{author}?category=X — filters by both author and category
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in Books:
        if book.get('author').casefold() == book_author.casefold() and \
                book.get('category').casefold() == category.casefold():  # casefold makes the comparison case-insensitive
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{book_title}")  # GET /books/{title} — finds a single book by title
async def read_books(book_title: str):
    for book in Books:
        if book.get('title').casefold() == book_title.casefold():
            return book  # returns the first matching book


@app.get("/books/mybook")  # GET /books/mybook — returns a hardcoded favorite book
async def read_all_books():
    return {'book_title': 'My Favorite Book'}


@app.get("/books/{dynamic_path}")  # GET /books/{anything} — generic catch-all path handler
async def read_all_books(dynamic_path: str):
    return {"message": f"You are reading {dynamic_path}"}


@app.get("/books/")  # GET /books/?category=X — filters all books by category query param
async def read_category_by_query(category: str):
    books_to_return = []
    for book in Books:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


@app.post("/books/create_book")  # POST /books/create_book — adds a new book from the request body
async def create_book(new_book=Body()):
    Books.append(new_book)  # appends the new book dict to the in-memory list
    return {"message": "Book created successfully"}


@app.put("/books/update_book")  # PUT /books/update_book — replaces a book matching the title in the request body
async def update_book(updated_book=Body()):
    for i in range(len(Books)):
        if Books[i].get('title').casefold() == updated_book.get('title').casefold():
            Books[i] = updated_book  # replace the old book dict with the updated one
            return {"message": "Book updated successfully"}
    return {"message": "Book not found"}


@app.delete("/books/delete_book")  # DELETE /books/delete_book?book_title=X — removes a book by title
async def delete_book(book_title: str):
    for i in range(len(Books)):
        if Books[i].get('title').casefold() == book_title.casefold():
            Books.pop(i)  # remove the book at index i from the list
            return {"message": "Book deleted successfully"}
    return {"message": "Book not found"}


@app.get("/books/author/{auth}")  # GET /books/author/{author} — returns all books by a specific author
async def fetch_books_by_author(auth: str):
    books_to_return = []
    for book in Books:
        if book.get('author').casefold() == auth.casefold():
            books_to_return.append(book)
    return books_to_return
