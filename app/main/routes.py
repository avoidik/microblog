from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language, UNKNOWN
from app import db
from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.models import User, Post
from app.translate import translate
from app.main import bp

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@bp.route("/search")
@login_required
def search():
    form = g.search_form
    if not form:
        return redirect(url_for("main.explore"))
    if not form.validate():
        if len(form.q.errors) > 0:
            flash(form.q.errors[0])
        return redirect(url_for("main.explore"))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(form.q.data, page, current_app.config["POSTS_PER_PAGE"])
    prev_url = url_for("main.search", q=form.q.data, page=page - 1) \
                if page > 1 else None
    next_url = url_for("main.search", q=form.q.data, page=page + 1) \
                if total > page * current_app.config["POSTS_PER_PAGE"] else None
    return render_template('search.html', title=_("Search"), posts=posts, next_url=next_url, prev_url=prev_url)

@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        lang = guess_language(form.post.data)
        if lang is UNKNOWN or len(lang) > 5:
            lang = ''
        post = Post(body=form.post.data, author=current_user, language=lang)
        db.session.add(post)
        db.session.commit()
        flash(_("Post added"))
        return redirect(url_for("main.index"))
    elif request.method == "GET":
        page = request.args.get('page', 1, type=int)
        posts = current_user.followed_posts(). \
                paginate(page, current_app.config['POSTS_PER_PAGE'], False)
        prev_url = url_for("main.index", page=posts.prev_num) \
                    if posts.has_prev else None
        next_url = url_for("main.index", page=posts.next_num) \
                    if posts.has_next else None
    return render_template("main/index.html", title=_("Home"),
                            form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()). \
            paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    prev_url = url_for("main.user", page=posts.prev_num, username=user.username) \
                if posts.has_prev else None
    next_url = url_for("main.user", page=posts.next_num, username=user.username) \
                if posts.has_next else None
    return render_template('main/user.html', title=_("Profile"),
                            user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Changes have been saved!"))
        return redirect(url_for("main.edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("main/edit_profile.html", title=_("Edit Profile"), form=form)

@bp.route("/follow/<username>")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_("User %(username)s is not found", username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_("You can not follow yourself"))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_("Now you are following %(username)s", username=username))
    return redirect(url_for('main.user', username=username))

@bp.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_("User %(username)s is not found", username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_("You can not unfollow yourself"))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_("Now you are not following %(username)s", username=username))
    return redirect(url_for('main.user', username=username))

@bp.route("/explore")
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query. \
            order_by(Post.timestamp.desc()). \
            paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    prev_url = url_for("main.explore", page=posts.prev_num) \
                if posts.has_prev else None
    next_url = url_for("main.explore", page=posts.next_num) \
                if posts.has_next else None
    return render_template("main/index.html", title=_("Explore"), posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route("/translate", methods=["POST"])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_lang'],
                                      request.form['dest_lang']
                                     )})
