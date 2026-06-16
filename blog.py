from fastapi import FastAPI, Request
from fastapi import Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import sessionmaker, Session

# Creates the SQLite database connection used by SQLAlchemy.
engine = create_engine(
    "sqlite:///blog.db",
    connect_args={"check_same_thread": False}
)

# SessionLocal creates database sessions for each request.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# FastAPI dependency: opens a DB session, gives it to the route, then closes it.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Base class for all SQLAlchemy models in this file.
class Base(DeclarativeBase):
    pass

# Blog table structure. Each object of this class represents one blog row.
class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(String(1000))
    author: Mapped[str] = mapped_column(String(50))

# Creates the table if it does not already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Tells FastAPI where the HTML template files are located.
templates = Jinja2Templates(directory="Frontend")

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    # Fetch all blog posts and send them to the home template.
    blogs = db.scalars(select(Blog)).all()

    return templates.TemplateResponse(
        name="index.html",
        context={"request": request, "blogs": blogs}
    )
    
@app.get("/create", response_class=HTMLResponse)
def create_page(request: Request):
    return templates.TemplateResponse(
        name="create.html"
        , context={"request": request}
    )


@app.post("/create")
def create_blog(
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form(...),
    db: Session = Depends(get_db)
):
    # Form values are converted into a Blog object, then saved in the database.
    new_blog = Blog(
        title=title,
        content=content,
        author=author
    )

    db.add(new_blog)
    db.commit()

    # 303 redirects the browser after a successful form submission.
    return RedirectResponse(url="/", status_code=303)


@app.get("/update/{blog_id}", response_class=HTMLResponse)
def update_page(
    request: Request,
    blog_id: int,
    db: Session = Depends(get_db)
):
    # Load the selected blog so the form can show its current values.
    blog = db.get(Blog, blog_id)

    return templates.TemplateResponse(
        name="update.html",
        context={"request": request, "blog": blog}
    )
    
    
@app.post("/update/{blog_id}")
def update_blog(
    blog_id: int,
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form(...),
    db: Session = Depends(get_db)
):
    blog = db.get(Blog, blog_id)

    if blog:
        # Update only if the blog exists.
        blog.title = title
        blog.content = content
        blog.author = author

        db.commit()

    return RedirectResponse(url="/", status_code=303)
    
@app.get("/delete-page/{blog_id}", response_class=HTMLResponse)
def delete_page(
    request: Request,
    blog_id: int,
    db: Session = Depends(get_db)
):
    # Shows a confirmation page before deleting the selected blog.
    blog = db.get(Blog, blog_id)

    return templates.TemplateResponse(
        name="delete.html",
        context={"request": request, "blog": blog}
    )    
    
@app.post("/delete/{blog_id}")
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db)
):
    blog = db.get(Blog, blog_id)

    if blog:
        # Remove the blog row from the database.
        db.delete(blog)
        db.commit()

    return RedirectResponse(url="/", status_code=303)
