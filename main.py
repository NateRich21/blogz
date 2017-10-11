from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post = db.Column(db.String(500))

    def __init__(self, title, post):
        self.title = title
        self.post = post


@app.route('/blog')
def index():

    entries = Entry.query.all() 
    return render_template('main-page.html', title="Build a Blog", entries=entries)

@app.route('/newpost')
def newpost_form():
    return render_template('add-new-post.html', title="Create Entry")

@app.route('/newpost', methods=['POST'])
def validate_post():
    title_error = ''
    post_error = ''
    post = ''
    title = ''

    request.method == 'POST'
    title = request.form['title']
    post = request.form['post']
    
    if title != '' and post != '':
        new_entry = Entry(title, post)
        db.session.add(new_entry)
        db.session.commit()
    
    if post == '':
        post_error = 'Please enter some content for your post'
    if title == '':
        title_error = 'Please enter a title for your new post'
 
    if not title_error and not post_error: 
        current_entry = Entry.query.filter_by(title=title).first()
        entry_id = current_entry.id
        return redirect("/entry?entry_id={}".format(entry_id))
    else:
        return render_template('add-new-post.html', title='Create Entry', 
        title_error=title_error, 
        post_error=post_error,
        post=post, entry_title=title)  

@app.route('/entry')
def display_post():
    entry_id = int(request.args.get('entry_id'))
    entry = Entry.query.get(entry_id)

    return render_template('post.html', entry=entry)


if __name__ == '__main__':
    app.run()   