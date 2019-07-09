from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:sm1979@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    content = db.Column(db.String(500))

    def __init__(self, name, content):
        self.name = name
        self.content = content

@app.route('/blog')
def home():
    
    blogs = Blog.query.all()
    id = request.args.get('id')
    if id:
        blog = Blog.query.filter_by(id=id).first()
        return render_template('blog.html', title="Home Page", blog=blog)
    else:
        return render_template('home.html', title="Home Page", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def index():

    blog_name_error = ''
    content_error = ''
    
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
            new_blog = Blog(blog_name, blog_content)
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