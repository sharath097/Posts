import time
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import mysql.connector
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

while True:
    try:
        connection = mysql.connector.connect(host="localhost",database="fastapi",user="root",password="Sh1r@th78")
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            print("Database connection was successfull!")
            break 
    except Exception as error:
        print(f"Connecting to database failed!\nError: {error}")
        time.sleep(2)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

# my_posts = [{"Id": 1, "Title": "Laptop", "Content": "Dell is a good company for Laptop"}, {"Id": 2, "Title": "Monitor", "Content": "BenQ is a good company for Monitor"}, {"Id": 3, "Title": "TV", "Content": "LG is a good company for TV"}]

# def find_post(id):
#     for post in my_posts:
#         if post["Id"] == id:
#             return post

# def find_index(id):
#     for index, post in enumerate(my_posts):
#         if post["Id"] == id:
#             return index

@app.get("/")
def root():
    return {"Message":"Hello World!"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return {"Status":"Successful"}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM POSTS """)
    # posts = cursor.fetchall()
    posts = db.query(models.Posts).all()
    return {"Posts":posts}

@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM POSTS WHERE ROW_ID = %s""", (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Posts).filter(models.Posts.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requested id: {id} was not found!")
    return {"Post": post}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    # cursor.execute(""" INSERT INTO POSTS(TITLE,CONTENT,PUBLISHED) VALUES(%s,%s,%s)""", (post.Title, post.Content, post.Publish))
    # connection.commit()
    # cursor.execute(""" SELECT * FROM POSTS WHERE ROW_ID = LAST_INSERT_ID() """)
    # new_post = cursor.fetchone()
    new_post = models.Posts(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"Post": new_post}

@app.put("/posts/{id}")
def update_post(id: int, update_post: Post, db: Session = Depends(get_db)):
    # cursor.execute(""" UPDATE POSTS SET TITLE = %s, CONTENT = %s, PUBLISHED = %s WHERE ROW_ID = %s""", (post.Title, post.Content, post.Publish, str(id),))
    # connection.commit()
    # cursor.execute(""" SELECT * FROM POSTS WHERE ROW_ID = %s """, (str(id),))
    # updated_post = cursor.fetchone()
    post_query = db.query(models.Posts).filter(models.Posts.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requested id: {id} was not found!")
    post_query.update(update_post.model_dump(), synchronize_session=False)
    db.commit()
    return {"post": post_query.first()}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM POSTS WHERE ROW_ID = %s """, (str(id),))
    # deleted_post = cursor.fetchone()
    # cursor.execute("""DELETE FROM POSTS WHERE ROW_ID = %s""", (str(id),))
    # connection.commit()
    post = db.query(models.Posts).filter(models.Posts.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requested id: {id} was not found!")
    post.delete(synchronize_session=False)
    db.commit()
