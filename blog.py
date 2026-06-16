from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Form, Depends
from fastapi.responses import RedirectResponse

# Database
engine = create_engine(
    "sqlite:///blog.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass

class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(String(1000))
    author: Mapped[str] = mapped_column(String(50))

Base.metadata.create_all(bind=engine)

# FastAPI
app = FastAPI()

templates = Jinja2Templates(directory="Frontend")

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
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
    new_blog = Blog(
        title=title,
        content=content,
        author=author
    )

    db.add(new_blog)
    db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.get("/update/{blog_id}", response_class=HTMLResponse)
def update_page(
    request: Request,
    blog_id: int,
    db: Session = Depends(get_db)
):
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
        db.delete(blog)
        db.commit()

    return RedirectResponse(url="/", status_code=303)