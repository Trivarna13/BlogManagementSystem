from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import create_engine
from sqlalchemy import text

engine = create_engine('mysql://@localhost/blog_db')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    bio = db.Column(db.Text, default=text("'Turning thoughts into digital ink'"))
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.following_id',
        backref=db.backref('following', lazy='joined'),
        lazy='dynamic'
    )
    following = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        backref='follower'
    )

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    likes = db.relationship('LikeDislike', backref='liked_post', primaryjoin="(Post.id == LikeDislike.post_id) & (LikeDislike.like == True)", cascade="all, delete-orphan")
    dislikes = db.relationship('LikeDislike', backref='disliked_post', primaryjoin="(Post.id == LikeDislike.post_id) & (LikeDislike.like == False)", cascade="all, delete-orphan")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


class LikeDislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id), nullable=False)  
    like = db.Column(db.Boolean, nullable=False)

    
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
