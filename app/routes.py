from flask import g, render_template, flash, redirect, url_for, send_file
from app import app
from app.forms import LoginForm, RegistrationForm, ContactForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Contact, Post, NewsLetter, Tag, Comment, File, PostCategory
from app import db
from flask import request
from functools import wraps
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
from app.forms import SearchForm, NewsLetterForm, CommentForm, FileUploadForm, ArticleForm
from io import BytesIO


# scripts to be loaded on each page
@app.before_request
def before_request():

    # ads scripts
    g.categories = PostCategory().query.all()

    # last seen logger
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


    

#error handlers
@app.errorhandler(404)
def file_not_found(error):
    db.session.rollback()
    return render_template('site/error/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    db.session.rollback()
    return render_template('site/error/500.html'), 500



@app.route('/user/like_post/post', methods=['POST', 'GET'])
def like_post():
    if current_user.is_anonymous:
        flash('You need to be logged in to like posts.', 'error')
        return redirect(request.form['next'])
    
    post = Post().query.get(int(request.form['postID']))
    if current_user.username == post.author:
        flash('Are you serious? You cannot like your own posts.', 'error')
        return redirect(request.form['next'])

    if request.method == 'POST':
        post.likes += 1
        db.session.commit()
        flash('You liked the post.', 'success')
        return redirect(request.form['next'])

#default homepage
@app.route('/')
@app.route('/index')
@app.route('/index.html')
@app.route('/home')
def index():
    featured = Post().query.order_by(Post.likes)
    newsletter_form = NewsLetterForm()
    return render_template('index.html', title='Home', newsletter_form=newsletter_form, featured=featured)




############################################
######   ADMIN     #########
############################################
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):

        if current_user.is_authenticated and current_user.email == 'rajatomar788@gmail.com':
            return func(*args, **kwargs)
        elif current_user.is_anonymous:
            return file_not_found(404)
            db.session.rollback()
        else:
            return file_not_found(404)
            db.session.rollback()
        return func(*args, **kwargs)
    return decorated_view

# admin functionality
@app.route('/admin', methods=['POST', 'GET'])
@app.route('/admin/comment_page/<int:comment_page>', methods=['POST', 'GET'])
@app.route('/admin/files_page/<int:files_page>', methods=['POST', 'GET'])
@app.route('/admin/requests_page/<string:request_page>', methods=['POST', 'GET'])
@admin_required
def admin(comment_page=1, files_page=1, request_page=1):
    pending_comments = Comment().query.filter_by(approved=0).order_by(Comment.timestamp.desc()).paginate(comment_page, app.config['POSTS_PER_PAGE'], False)
    uploaded_files = File().query.order_by(File.timestamp.desc()).paginate(files_page, app.config['POSTS_PER_PAGE'], False)
    contact_requests = Contact().query.order_by(Contact.timestamp.desc()).paginate(request_page, app.config['POSTS_PER_PAGE'], False)

    return render_template('site/admin/admin.html', title='Control Panel', pending_comments=pending_comments, contact_requests=contact_requests, uploaded_files=uploaded_files)

@app.route('/approve_comment/<int:commentID>')
@admin_required
def approve_comment(commentID):
    comment = Comment().query.get(int(commentID))
    comment.approved = '1'
    db.session.commit()
    flash('Comment Approved !', 'success')
    return redirect(url_for('admin'))
@app.route('/delete_comment/<int:commentID>')
@admin_required
def delete_comment(commentID):
    comment = Comment().query.get(int(commentID))
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully !', 'success')
    return redirect(url_for('admin'))
@app.route('/view_file/<int:fileID>')
@admin_required
def view_file(fileID):
    f = File().query.get(int(fileID))
    return send_file(BytesIO(f.filedata), attachment_filename=f.filename)
@app.route('/delete_file/<int:fileID>')
@admin_required
def delete_file(fileID):
    f = File().query.get(int(fileID))
    db.session.delete(f)
    db.session.commit()
    flash('File Deleted successfully !', 'success')
    return redirect(url_for('admin'))

@app.route('/reply_contact/<int:contactID>')
@admin_required
def reply_contact(contactID):
    contact = File().query.get(int(contactID))
    return render_template('site/admin/reply_contact.html', title="Reply Request" , contact=contact)

@app.route('/delete_contact/<int:contactID>')
@admin_required
def delete_contact(contactID):
    contact = Contact().query.get(int(contactID))
    db.session.delete(contact)
    db.session.commit()
    flash('Contact Request Deleted successfully !', 'success')
    return redirect(url_for('admin'))

#########################################
######################################################



#user login
@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User.query.filter_by(email=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('site/login.html', title="Sign In", form=form)
#logout user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
#user registration
@app.route('/register', methods=['GET', 'POST'])
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, fullname=form.fullname.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('site/register.html', title='Register', form=form)
#user profiles
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=username).order_by(Post.timestamp.desc()).all()
    return render_template('site/user.html', user=user, posts=posts, title=username)
#user profile editor
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.fullname = form.fullname.data
        current_user.hobby = form.hobby.data
        current_user.occupation = form.occupation.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('user', username=current_user.username))

    elif request.method == 'GET':
        form.fullname.data = current_user.fullname
        form.hobby.data = current_user.hobby
        form.occupation.data = current_user.occupation
        form.about_me.data = current_user.about_me

    return render_template('user/edit_profile.html', title='Edit Profile', form=form)

#contact request adder
@app.route('/contact', methods=['GET', 'POST'])
@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact_request = Contact(name=form.name.data, email=form.email.data, company=form.company.data, message=form.message.data)
        db.session.add(contact_request)
        db.session.commit()
        flash('Your contact request have been posted. Admins will contact you shortly.', 'success')
        return redirect(url_for('contact'))
    return render_template('site/contact.html', title='Contact', form=form)

#license and things
@app.route('/about')
@app.route('/about.html')
def about():

    return render_template('site/about.html', title='About')


#file upload system
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploader', methods=['POST', 'GET'])
@login_required
def uploader():
    form = FileUploadForm()


    if request.method == 'POST': 

        if 'inputfile' not in request.files:
            flash('No File Part !' , 'error')
            return redirect(request.url)


        f = request.files['inputfile']

        if f.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if not allowed_file(f.filename):
            flash('File type not Supported ! Please contact administrator if you want to do so.', 'error')
            return redirect(request.url)

        # final check of file and saving and indexing
        if f and allowed_file(f.filename):
            f.filename = secure_filename(f.filename)

            fileindex = File(filename=f.filename, filedata=f.read(), user_id=current_user.id)

            db.session.add(fileindex)
            db.session.commit()

            fileID = File().query.filter_by(filename=f.filename).first()

            flash('File uploaded successfully !', 'success')
            return redirect(url_for('uploaded_file', fileID=fileID.id))
    return render_template('site/fileupload.html', title='Upload Files', form=form)

@app.route('/uploaded_file/<int:fileID>')
@login_required
def uploaded_file(fileID):
    file = File().query.get(int(fileID))
    if file is None or file.user_id != current_user.id:
        flash("You don't have permission to view this page !", 'error')
    else:
        fileurl = 'https://chemicallocha.herokuapp.com/site/uploads/' + file.filename
        return render_template('site/fileupload.html', title='File Uploaded Successfully' , filename=file.filename, fileurl=fileurl)

#file fetching system
@app.route('/site/uploads/<string:filename>')
def uploads(filename):
    if filename is None or filename == '':
        return None
    else:
        f = File().query.filter_by(filename=filename).first()
        return send_file(BytesIO(f.filedata), attachment_filename=f.filename)




#subscriber adder
@app.route('/add_subscriber', methods=['POST', 'GET'])
def add_subscriber():
    if request.method == 'POST':
        next_page = request.form['next_page']
        if NewsLetter().query.filter_by(email=request.form['email']).first() is None:
            subscriber = NewsLetter(email=request.form['email'])
            db.session.add(subscriber)
            db.session.commit()
            flash('You have been successfully added to our mailing list.', 'success')

        elif request.form['email'] == '':
            flash('Please Enter a valid Email Address !', 'error')

        else:
            flash('You are already in our mailing list. Thank You!', 'message')
    return redirect(next_page)

####################### user dashboard ########################################

@app.route('/dashboard')
@login_required
def dashboard():
    posts = Post().query.filter_by(author=current_user.username).all()
    pending_comments = Comment().comments_on_user_posts(current_user.id)
    return render_template('user/dashboard.html', posts=posts, title='Dashboard', pending_comments=pending_comments)

@app.route('/approve_comment_user/<int:commentID>')
@login_required
def approve_comment_user(commentID):
    comment = Comment().query.get(int(commentID))
    comment.approved = '1'
    db.session.commit()
    flash('Comment Approved !', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_comment_user/<int:commentID>')
@login_required
def delete_comment_user(commentID):
    comment = Comment().query.get(int(commentID))
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully !', 'success')
    return redirect(url_for('dashboard'))

@app.route('/view_file_user/<int:fileID>')
@login_required
def view_file_user(fileID):
    f = File().query.get(int(fileID))
    return send_file(BytesIO(f.filedata), attachment_filename=f.filename)

@app.route('/delete_file_user/<int:fileID>')
@login_required
def delete_file_user(fileID):
    f = File().query.get(int(fileID))
    db.session.delete(f)
    db.session.commit()
    flash('File Deleted successfully !', 'success')
    return redirect(url_for('dashboard'))

#######################   user dashboard end ##################




# add article
@app.route('/add_article', methods=['POST', 'GET'])
@login_required
def add_article():
    form = ArticleForm()
    postcategories =  PostCategory().query.all()
    tags = Tag().query.all()

    if form.validate_on_submit():
        category = PostCategory().query.filter_by(category_name=request.form['post-category-selector']).first()
        
        article = Post(heading=form.heading.data, author=current_user.username, timestamp=datetime.utcnow(), body=form.body.data, thumbnail=request.form['thumbnail'])

        string = request.form['tags'] + ','
        tag_list = []
        char = []
        for i in string:
            if i != ',':
                char.append(i)
            elif i == ',':
                char = ''.join(char)
                char = char.strip()
                get_tag = Tag.query.filter_by(tag_name=char).first()
                if get_tag is not None:
                    tag_list.append(get_tag)
                elif get_tag is None:
                    Tag().new_tag(char)
                    get_tag = Tag.query.filter_by(tag_name=char).first()
                    if get_tag is not None:
                        tag_list.append(get_tag)

                char = [] 

        article.tags = tag_list
        category.posts.append(article)
        db.session.commit()
        flash('Your Article has been successfully added !', 'success')
        return redirect(url_for('dashboard'))
    return render_template('user/add_article.html', title='Add Article', form=form, postcategories=postcategories,tags=tags)


@app.route('/confirm_delete/<int:postID>')
@login_required
def confirm_delete(postID):
    post = Post().query.get(int(postID))
    if post.author == current_user.username and Post().query.get(int(postID)) is not None:
        return render_template('user/delete_article.html', title='Confirm Deletion of your Post', post=post)
    else:
        flash("You don't have permission to delete this post.\n If you want to do so contact the Administrators.", 'error')
        return redirect(url_for('dashboard'))



# delete article
@app.route('/delete_article/<int:postID>')
@login_required
def delete_article(postID):
    post = Post.query.get(int(postID))

    if post.author == current_user.username:
        post.tags = []
        db.session.flush()
        db.session.delete(post)
        db.session.commit()
        flash('Your post has been successfully deleted !', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash("You don't have permission to delete this post.\n If you want to do so contact the Administrators.", 'error')
        return redirect(url_for('dashboard'))

# edit articles
@app.route('/edit_article/<int:postID>', methods=['POST','GET'])
@login_required
def edit_article(postID):
    post = Post().query.get(int(postID))
    form = ArticleForm()
    if not post:
        flash('No such article Found !', 'error')
        return redirect(url_for('file_not_found(404)'))

    if current_user.username == post.author:
        if form.validate_on_submit():
            post.heading = form.heading.data
            post.body = form.body.data
            post.timestamp = datetime.utcnow()
            db.session.commit()
            flash('Your article has been successfully updated !', 'success')
            return redirect(url_for('dashboard'))  
        elif request.method == 'GET':
            form.heading.data = post.heading
            form.body.data = post.body
        return render_template('user/edit_article.html', post=post, title='Edit Article', form=form)
    else:
        flash('You are not the author of this article.\n If you want any changes in this article please contact Administrator through Contact Page.', 'error')
        return redirect(url_for('blog'))

#blog homepage
@app.route('/blog/')
@app.route('/blog/page/<int:page>')
def blog(page=1):
    categories = PostCategory().query.all()
    tags=Tag().query.all()
    featured = Post().query.order_by(Post.likes)
    latest = Post().latest_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    return render_template('site/blog.html', title='Blog', latest=latest, featured_posts=featured, post_categories=categories, tags=tags)

@app.route('/add_article', methods=['POST'])

#blog posts by id
@app.route('/blog/post/<int:postID>', methods=['POST', 'GET'])
def show_post(postID):
    categories = PostCategory().query.all()
    post = Post().query.get(int(postID))
    if post.post_url is not None:
        article = post.post_url
    else:
        article = 'site/post.html'

    newsletter_form = NewsLetterForm()
    comments = Comment.query.filter_by(post_id=postID).all()
    ref='blog/post/' + str(postID)
    # comment adder
    commentform = CommentForm()
    if commentform.validate_on_submit():
        comment = Comment(comment=commentform.comment.data, post_id=post.id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been successfully added and pending Administrators approval to get live on blog.')
        return redirect(ref)
    try:
    	return render_template('site/post.html', title=post.heading, post=post, newsletter_form=newsletter_form, commentform=commentform, comments=comments, ref=ref, post_categories=categories)
    except:
       return file_not_found(404)

@app.route('/blog/post/categories')
@app.route('/blog/post/tags')
def post_catalog():
    categories = PostCategory().query.all()
    tags=Tag().query.all()
    return render_template('site/post/post_catalog.html', post_categories=categories, tags=tags)

@app.route('/blog/post/category/<categoryID>')
def post_category(categoryID):
    tags=Tag().query.all()
    category = PostCategory().query.get(int(categoryID))
    if category is None:
        return file_not_found(404)
    posts = category.posts
    return render_template('site/post/post_category.html', posts=posts, category=category, tags=tags)
@app.route('/blog/post/tag/<tagID>')
def post_tag(tagID):
    tag = Tag().query.get(int(tagID))
    if tag is None:
        return file_not_found(404)
    posts =  tag.posts
    return render_template('site/post/post_tag.html', posts=posts, tag=tag)

@app.route('/add_post_catalog')
@login_required
def add_post_catalog():
    return render_template('site/post/add_post_catalog.html')

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    if request.method == 'POST':
        category = PostCategory().query.filter_by(category_name=request.form['category']).first()
        if category is None:
            category = PostCategory(category_name=request.form['category'])
            db.session.add(category)
            db.session.commit()
            flash('Category added Successfully!', 'success')
        else: 
            flash('Category already exists!', 'alert')
        return render_template('site/post/add_post_catalog.html')

@app.route('/add_tag', methods=['POST'])
@login_required
def add_tag():
    if request.method == 'POST':
        tag = Tag().query.filter_by(tag_name=request.form['tag']).first()
        if tag is None:
            tag = Tag(tag_name=request.form['tag'])
            db.session.add(tag)
            db.session.commit()
        
            flash('Tag added Successfully', 'success')
        else:
            flash('Tag already exists!', 'alert')
        return render_template('site/post/add_post_catalog.html')