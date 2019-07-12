from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:sm1979@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'Darvette1235'
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    content = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, content, owner):
        self.name = name
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogz = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    print('**************************************************')
    print(session)
    print('**************************************************')
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #validate
        existing_user = User.query.filter_by(username=username).first()

        if len(username) < 3:
            flash('username invalid')
            return redirect('/signup')


        if len(password) < 3:
            flash('password invalid')
            return redirect('/signup')

        if  existing_user:
            flash('username already exists')
            return redirect('/signup')

        if (not username) or (not password) or (not verify):
            flash('one or more fields invalid')
            return redirect('/signup')

        if not (password == verify):
            flash('passwords do not match')
            return redirect('/signup')
            
        if len(password) < 3:
            flash('password invalid')
            return redirect('/signup')

        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        #"remember" that the user has registered
        session['username'] = username
        return redirect('/newpost')

    return render_template('signup.html', title="Signup")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('username does not exist')
            return redirect('/login')
        if not (user.password == password):
            flash('password incorrect')
            return redirect('/login')

        #"remember" that the user has logged in
        session['username'] = username
        flash('Loggeed in')
        print(session)
        return redirect('/newpost')

    return render_template('login.html', title="Log In")


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/blog')
def blog():
    #owner = User.query.filter_by(username=session['username']).first()
    blogs = Blog.query.all()
    id = request.args.get('id')
    if id:
        blog = Blog.query.filter_by(id=id).first()
        return render_template('blog.html', title="Blog Page", blog=blog)
    else:
        return render_template('list_blog.html', title="Blogs Page", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    blog_name_error = ''
    content_error = ''
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_name = request.form['blog']
        blog_content = request.form['content'].strip()
        print("********************" + str(len(blog_content)) + "*********************")
        print("********************" + blog_content + "*********************")
        if len(blog_name) < 1:
            blog_name_error = 'Blog must have a name'
        if len(blog_content) < 1:
            content_error = 'Blog must have a message'
        if not content_error and not blog_name_error:
            new_blog = Blog(blog_name, blog_content, owner)
            db.session.add(new_blog)
            db.session.commit()
            id = str(new_blog.id)
            print("********************" + id + "*********************")
            return redirect('/blog?id={}'.format(id))
       
        return render_template('post.html', title="Build a Blog", content=blog_content, blog_name=blog_name, blog_name_error=blog_name_error, content_error=content_error)
           
    return render_template('post.html', title="Build a Blog")
#@app.route('/delete-task', methods=['POST'])
#def delete_task():

#   task_id = int(request.form['task-id'])
#   task = Task.query.get(task_id)
#   task.completed = True
#   db.session.add(task)
#   db.session.commit()

#   return redirect('/')

if __name__ == '__main__':
    app.run()