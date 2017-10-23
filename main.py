from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:blog@localhost:8889/Blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "yK2Blog"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog')
def blog():
    user_id = request.args.get('user_id')
    entry_id = request.args.get('entry_id')
    entries = Blog.query.all()
    users = User.query.all()
    
    if user_id:
        user_id = int(user_id)
        entries = Blog.query.filter_by(owner_id=user_id).all()
    if entry_id:
        entry_id = int(entry_id)
        entries = Blog.query.filter_by(id=entry_id).all()

    return render_template('main-page.html', title="Build a Blog", entries=entries, 
    entry_id=entry_id, users=users)

@app.route('/newpost')
def newpost_form():
    return render_template('add-new-post.html', title="Create Blog")

@app.route('/newpost', methods=['POST'])
def validate_post():
    title_error = ''
    post_error = ''
    post = ''
    title = ''

    request.method == 'POST'
    title = request.form['title']
    post = request.form['post']
    owner = User.query.filter_by(username=session['username']).first()
    
    
    if title != '' and post != '':
        new_entry = Blog(title, post, owner)
        db.session.add(new_entry)
        db.session.commit()
    
    if post == '':
        post_error = 'Please enter some content for your post'
    if title == '':
        title_error = 'Please enter a title for your new post'
 
    if not title_error and not post_error: 
        current_entry = Blog.query.filter_by(title=title).first()
        entry_id = current_entry.id
        return redirect("/blog?entry_id={}".format(entry_id))
    else:
        return render_template('add-new-post.html', title='Create Blog', 
        title_error=title_error, 
        post_error=post_error,
        post=post, entry_title=title)  
        

@app.route('/login', methods=['POST', 'GET'])
def login():
    login_error = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] 
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        elif user and user.password != password:
            login_error = 'The password is incorrect for this username'
            return render_template('login.html', title="Login", login_error=login_error)
        else:
            login_error = 'Username not found'
            return render_template('login.html', title="Login", login_error=login_error)
            
    return render_template('login.html', title="Login")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        name_error = ''
        password_error = ''
        verify_error = ''
        if not username or len(username) < 3 or len(username) > 16:
            name_error = "Please enter a valid username"
        if not password or len(password) < 3 or len(password) > 16:
            password_error = "Please enter valid password"
            password = ''
        if not verify:
            verify_error = "Please verify password"
            verify = ''
        elif verify != password:
            verify_error = 'Passwords do not match'
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            name_error = "This username is not available"

        if not existing_user and not name_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', name_error=name_error,
            password_error=password_error,
            verify_error=verify_error)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/')
def index():
    users = User.query.all()

    return render_template('index.html', title='Home', users=users)


if __name__ == '__main__':
    app.run()