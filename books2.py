from fastapi import FastAPI, Path, Query, HTTPException  # Path validates path params; Query validates query params; HTTPException returns error responses
from pydantic import BaseModel, Field  # BaseModel defines request/response schemas; Field adds validation rules
from typing import Optional  # Optional marks a field as not required
from starlette import status  # status provides HTTP status code constants like 200, 201, 204

app = FastAPI()  # create the FastAPI application instance


class Book:  # plain Python class representing a book object (not a DB model, just in-memory)
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):  # constructor to create a Book instance
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):  # Pydantic model used to validate incoming request body data
    id: Optional[int] = Field(description="ID of the book (optional)", default=None)  # id is optional — auto-assigned on create
    title: str = Field(min_length=3)  # title must be at least 3 characters
    author: str = Field(min_length=1)  # author must be at least 1 character
    description: str = Field(min_length=1, max_length=100)  # description between 1 and 100 characters
    rating: int = Field(gt=0, lt=6)  # rating must be between 1 and 5 (exclusive of 0 and 6)
    published_date: int = Field(gt=1999, lt=2025)  # published year must be between 2000 and 2024

    model_config = {
        "json_schema_extra": {  # provides example data shown in the /docs Swagger UI
            "examples": [{
                "title": "A new Book",
                "author": "coding with Rajesh",
                "description": "A new Book Description",
                "rating": 5,
                "published_date": 2023
            }]
        }
    }


# in-memory list of Book objects acting as a temporary database
Books = [
    Book(1, 'Computer Science Prob', 'codingwithroby', 'A very nice book', 4, 2023),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book', 4, 2024),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A Awesome book', 4, 2025),
    Book(4, 'HP1', 'codingwithRajesh', 'Book description', 4, 2022),
    Book(5, 'HP2', 'codingwithRajesh', 'Book description', 3, 2021),
    Book(6, 'Hp3', 'codingwithRajesh', 'Book description', 2, 2020)
]


@app.get("/books", status_code=status.HTTP_200_OK)  # GET /books — returns all books with 200 OK
def read_all_books():
    return Books


@app.get("/books/published")  # GET /books/published?published_date=X — filters books by published year
def read_book_by_published_date(published_date: int):
    books_to_return = []
    for book in Books:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{book_id}")  # GET /books/{id} — returns a single book by its ID
def read_book(book_id: int = Path(gt=0)):  # Path(gt=0) ensures book_id must be greater than 0
    for book in Books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")  # raise 404 if no match found


@app.get("/books/", status_code=status.HTTP_200_OK)  # GET /books/?rating=X — filters books by rating
def read_book_by_rating(rating: int = Query(gt=0, lt=6)):  # Query validates rating is between 1 and 5
    books_to_return = []
    for book in Books:
        if book.rating == rating:
            books_to_return.append(book)
    return books_to_return


@app.post("/books/create_book", status_code=status.HTTP_201_CREATED)  # POST /books/create_book — creates a new book, returns 201 Created
def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())  # model_dump() converts the Pydantic model to a dict; ** unpacks it as keyword arguments into the Book constructor
    print(new_book)
    Books.append(find_book_id(new_book))  # auto-assign an ID before appending to the list


def find_book_id(book: Book):  # helper function that assigns the next available ID to a new book
    if len(Books) > 0:
        book.id = Books[-1].id + 1  # set ID to last book's ID + 1
    else:
        book.id = 1  # if list is empty, start from 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)  # PUT /books/update_book — updates an existing book, returns 204 No Content
def update_book(book_request: BookRequest):
    book_changed = False  # flag to track if a matching book was found and updated
    book = Book(**book_request.model_dump())  # convert request body to a Book object
    print(book)
    for i in range(len(Books)):
        if Books[i].id == book.id:
            Books[i] = book  # replace the old book with the updated one
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Book not found")  # raise 404 if no book matched the given ID


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)  # DELETE /books/{id} — deletes a book by ID, returns 204 No Content
def delete_book(book_id: int = Path(gt=0)):  # Path(gt=0) ensures book_id must be greater than 0
    book_changed = False  # flag to track if a matching book was found and deleted
    for i in range(len(Books)):
        if Books[i].id == book_id:
            Books.pop(i)  # remove the book at index i from the list
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Book not found")  # raise 404 if no book matched the given ID
