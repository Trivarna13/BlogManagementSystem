from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, login_user
from .models import Post, User, Comment, LikeDislike, Follow
from . import db
from sqlalchemy import func

views = Blueprint("views", __name__)

@views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        if not email or not username or not password1 or not password2:
            flash('All fields are required.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        else:
            new_user = User(email=email, username=username, password=password1)
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully!', category='success')
            login_user(new_user)
            return redirect(url_for('views.home'))
    
    return render_template('signup.html', user=current_user)


@views.route("/")
@views.route("/home")
@login_required
def home():
    user_id = current_user.id
    user_blog_posts = Post.query.filter_by(author_id=user_id).all()

    all_blog_posts = Post.query.all()
    authors = {post.id: User.query.get(post.author_id).username for post in all_blog_posts}
    
    post_comments = {post.id: Comment.query.filter_by(post_id=post.id).all() for post in all_blog_posts}
    
    post_likes_count = {}
    post_dislikes_count = {}

    for post in all_blog_posts:
        likes_count = db.session.query(func.count(LikeDislike.id)).filter(LikeDislike.post_id == post.id, LikeDislike.like == True).scalar()
        dislikes_count = db.session.query(func.count(LikeDislike.id)).filter(LikeDislike.post_id == post.id, LikeDislike.like == False).scalar()
        post_likes_count[post.id] = likes_count
        post_dislikes_count[post.id] = dislikes_count

    return render_template("home.html", user=current_user, user_blog_posts=user_blog_posts, all_blog_posts=all_blog_posts, db=db, authors=authors, post_comments=post_comments, post_likes_count=post_likes_count, post_dislikes_count=post_dislikes_count)

@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author_id=current_user.id)

            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)


@views.route("/delete-post/<int:id>", methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = Post.query.get(id)

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author_id:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/user-profile/<username>")
def user_profile(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))
    
    all_blog_posts = Post.query.all()
    
    post_likes_count = {}
    post_dislikes_count = {}

    for post in all_blog_posts:
        likes_count = db.session.query(func.count(LikeDislike.id)).filter(LikeDislike.post_id == post.id, LikeDislike.like == True).scalar()
        dislikes_count = db.session.query(func.count(LikeDislike.id)).filter(LikeDislike.post_id == post.id, LikeDislike.like == False).scalar()
        post_likes_count[post.id] = likes_count
        post_dislikes_count[post.id] = dislikes_count
    return render_template("user_profile.html", user=user, post_likes_count=post_likes_count, post_dislikes_count=post_dislikes_count)  

@views.route("/view-user-profile/<username>")
def view_user_profile(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))
    
    all_blog_posts = Post.query.all()
    followers_count = db.session.query(func.count(Follow.id)).filter(Follow.following_id == user.id).scalar()
    following_count = db.session.query(func.count(Follow.id)).filter(Follow.follower_id == user.id).scalar()
    
    post_likes_count = {}
    post_dislikes_count = {}

    for post in all_blog_posts:
        likes_count = db.session.query(func.count(LikeDislike.id)).filter(LikeDislike.post_id == post.id, LikeDislike.like == True).scalar()
        dislikes_count = db.session.query(func.count(LikeDislike.id)).filter(LikeDislike.post_id == post.id, LikeDislike.like == False).scalar()
        post_likes_count[post.id] = likes_count
        post_dislikes_count[post.id] = dislikes_count
    return render_template("view_user_profile.html", user=user,followers_count=followers_count, following_count=following_count,  post_likes_count=post_likes_count, post_dislikes_count=post_dislikes_count)

@views.route('/edit-user-profile', methods=['GET', 'POST'])
@login_required
def edit_user_profile():
    user = User.query.get(current_user.id)

    if request.method == 'POST':
        bio = request.form.get('bio')
        new_username = request.form.get('username') 
        user.bio = bio
        user.username = new_username 

        db.session.commit()
        return redirect(url_for('views.user_profile', username=user.username))

    return render_template('edit_user_profile.html', user=current_user, user_profile=user)


@views.route("/create-comment/<int:post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.get(post_id)
        if post:
            comment = Comment(text=text, author_id=current_user.id, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))

@views.route("/delete-comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author.id and current_user.id != comment.post.author.id:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))

@views.route("/like-post/<int:post_id>", methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get(post_id)

    if not post:
        flash('Post does not exist.', category='error')
    else:
        existing_like = LikeDislike.query.filter_by(user_id=current_user.id, post_id=post_id, like=True).first()
        existing_dislike = LikeDislike.query.filter_by(user_id=current_user.id, post_id=post_id, like=False).first()

        if existing_like:
            db.session.delete(existing_like)
        else:
            like = LikeDislike(user_id=current_user.id, post_id=post_id, like=True)
            db.session.add(like)

            if existing_dislike:
                db.session.delete(existing_dislike)

        db.session.commit()

    return redirect(url_for('views.home'))

@views.route("/dislike-post/<int:post_id>", methods=['POST'])
@login_required
def dislike_post(post_id):
    post = Post.query.get(post_id)

    if not post:
        flash('Post does not exist.', category='error')
    else:
        existing_like = LikeDislike.query.filter_by(user_id=current_user.id, post_id=post_id, like=True).first()
        existing_dislike = LikeDislike.query.filter_by(user_id=current_user.id, post_id=post_id, like=False).first()

        if existing_dislike:
            db.session.delete(existing_dislike)
        else:
            dislike = LikeDislike(user_id=current_user.id, post_id=post_id, like=False)
            db.session.add(dislike)

            if existing_like:
                db.session.delete(existing_like)

        db.session.commit()

    return redirect(url_for('views.home'))


@views.route("/follow/<int:user_id>", methods=['POST'])
@login_required
def follow_user(user_id):
    user_to_follow = User.query.get(user_id)

    if not user_to_follow:
        flash('User does not exist.', category='error')
    elif user_to_follow == current_user:
        flash('You cannot follow yourself.', category='error')
    else:
        existing_follow = Follow.query.filter_by(follower_id=current_user.id, following_id=user_id).first()

        if not existing_follow:
            follow = Follow(follower_id=current_user.id, following_id=user_id)
            db.session.add(follow)
            db.session.commit()

    return redirect(url_for('views.view_user_profile', username=user_to_follow.username))


@views.route("/unfollow/<int:user_id>", methods=['POST'])
@login_required
def unfollow_user(user_id):
    user_to_unfollow = User.query.get(user_id)

    if not user_to_unfollow:
        flash('User does not exist.', category='error')
    else:
        existing_follow = Follow.query.filter_by(follower_id=current_user.id, following_id=user_id).first()

        if existing_follow:
            db.session.delete(existing_follow)
            db.session.commit()

    return redirect(url_for('views.view_user_profile', username=user_to_unfollow.username))


