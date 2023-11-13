from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import shutil

from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy()

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


# Определение модели пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

# Decorate a function with the app context
def initialize_database():
    with app.app_context():
        # Create the database tables
        db.create_all()






import glob

# @app.route('/')
# def index():
#     files = []
#     if 'username' in session:
#         username = session['username']
#         user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
#         if os.path.exists(user_folder):
#             files = os.listdir(user_folder)
#     total_files = len(glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '**', '*'), recursive=True))
#     return render_template('index.html', files=files, total_files=total_files)
@app.route('/')
def index():
    files = []
    folder_exists = False

    if 'username' in session:
        username = session['username']
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
        if os.path.exists(user_folder):
            files = os.listdir(user_folder)
            folder_exists = any(os.path.isdir(os.path.join(user_folder, file)) for file in files)

    total_files = len(glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '**', '*'), recursive=True))
    return render_template('index.html', files=files, total_files=total_files, folder_exists=folder_exists)

@app.route('/open-folder/<folder_name>')
def open_folder(folder_name):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    folder_path = os.path.join(user_folder, folder_name)

    if os.path.isdir(folder_path):
        files = []
        folders = []

        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                files.append(item)
            elif os.path.isdir(item_path):
                folders.append(item)

        return render_template('folder.html', folder_name=folder_name, files=files, folders=folders)
    else:
        flash('Folder not found')
        return redirect(url_for('index'))

@app.route('/open-subfolder/<folder_name>/<subfolder_name>')
def open_subfolder(folder_name, subfolder_name):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    folder_path = os.path.join(user_folder, folder_name, subfolder_name)

    if os.path.isdir(folder_path):
        files = []
        folders = []

        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                files.append(item)
            elif os.path.isdir(item_path):
                folders.append(item)

        return render_template('subfolder.html', folder_name=folder_name, subfolder_name=subfolder_name, files=files, folders=folders)
    else:
        flash('Subfolder not found')
        return redirect(url_for('open_folder', folder_name=folder_name))



@app.route('/upload-file/<folder_name>/<subfolder_name>', methods=['POST'])
def upload_file_in_folder(folder_name, subfolder_name):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    folder_path = os.path.join(user_folder, folder_name, subfolder_name)

    if not os.path.exists(folder_path):
        flash('Folder not found')
        return redirect(url_for('open_subfolder', folder_name=folder_name, subfolder_name=subfolder_name))

    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('open_subfolder', folder_name=folder_name, subfolder_name=subfolder_name))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('open_subfolder', folder_name=folder_name, subfolder_name=subfolder_name))

    filename = secure_filename(file.filename)
    file_path = os.path.join(folder_path, filename)
    file.save(file_path)

    flash('File uploaded successfully')
    return redirect(url_for('open_subfolder', folder_name=folder_name, subfolder_name=subfolder_name))


@app.route('/upload-file/<folder_name>', methods=['POST'])
def upload_file(folder_name):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    folder_path = os.path.join(user_folder, folder_name)

    if not os.path.exists(folder_path):
        flash('Folder not found')
        return redirect(url_for('index'))

    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('open_folder', folder_name=folder_name))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('open_folder', folder_name=folder_name))

    filename = secure_filename(file.filename)
    file_path = os.path.join(folder_path, filename)
    file.save(file_path)

    flash('File uploaded successfully')
    return redirect(url_for('open_folder', folder_name=folder_name))


# from flask import Markup
from markupsafe import Markup

@app.template_filter('check_if_directory')
def check_if_directory(file):
    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    file_path = os.path.join(user_folder, file)

    if os.path.isdir(file_path):
        return Markup(file)  # Используйте Markup, чтобы отобразить имя файла как HTML-код

    return None

@app.route('/delete-folder/<folder_name>')
def delete_folder(folder_name):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    folder_path = os.path.join(user_folder, folder_name)

    if os.path.isdir(folder_path):
        # Удаление папки и её содержимого
        shutil.rmtree(folder_path)
        # flash('Folder deleted successfully')
    else:
        flash('Folder not found')

    return redirect(url_for('index'))

import re

@app.route('/create_subfolder/<folder_name>', methods=['POST'])
def create_subfolder(folder_name):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    folder_path = os.path.join(user_folder, folder_name)
    subfolder_name = request.form['subfolder_name']
    subfolder_path = os.path.join(folder_path, subfolder_name)

    if re.search(r'[<>:"/\\|?*]', subfolder_name):
        flash("Имя папки содержит запрещенные символы.")
        return redirect(url_for('open_folder', folder_name=folder_name))

    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)
        flash('Subfolder created successfully')
    else:
        flash('Subfolder already exists')

    return redirect(url_for('open_folder', folder_name=folder_name))

def check_if_username_exists(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return True
    return False



from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None  # Переменная для хранения сообщения об ошибке
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if len(password) < 6:
            error = 'Пороль: Не менше 6 символів'
            return render_template('register.html', error=error)

        elif User.query.filter_by(username=username).first() is not None:
            error = 'Ім`я користувача вже існує'
            return render_template('register.html', error=error)
        
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            
            user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
            os.makedirs(user_folder, exist_ok=True)
            
            return redirect(url_for('login'))
    
    return render_template('register.html', error=error)  # Передаем ошибку в шаблон




import re

@app.route('/create-folder', methods=['POST'])
def create_folder():
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    folder_name = request.form['folder_name']
    folder_path = os.path.join(user_folder, folder_name)

    if re.search(r'[<>:"/\\|?*]', folder_name):
        flash("Имя папки содержит запрещенные символы.")
        return redirect(url_for('index'))

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        flash('Folder created successfully')
    else:
        flash('Folder already exists')

    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        session['username'] = username
        # flash('Login successful')
        return redirect(url_for('index'))
    
    return render_template('login.html')



# from werkzeug.security import check_password_hash

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         user = User.query.filter_by(username=username, password=password).first()
#         if user is None:
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
        
#         session['username'] = username
#         # flash('Login successful')
#         return redirect(url_for('index'))
    
#     return render_template('login.html')





@app.route('/account', methods=['GET', 'POST'])
def account():
    files = []
    if 'username' in session:
        username = session['username']
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
        if os.path.exists(user_folder):
            files = os.listdir(user_folder)
    return render_template('account.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    # flash('Logged out')
    return redirect(url_for('index'))


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))
    
    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    filename = secure_filename(file.filename)
    file_path = os.path.join(user_folder, filename)
    file.save(file_path)
    
    # flash('File uploaded successfully')
    return redirect(url_for('index'))


@app.route('/delete/<filename>')
def delete(filename):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))
    
    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    file_path = os.path.join(user_folder, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        # flash('File deleted successfully')
    else:
        flash('File not found')
    
    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download(filename):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))
    
    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    file_path = os.path.join(user_folder, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('File not found')
        return redirect(url_for('index'))

@app.route('/delete-file/<folder_name>/<filename>')
def delete_file(folder_name, filename):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    file_path = os.path.join(user_folder, folder_name, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully')
    else:
        flash('File not found')

    return redirect(url_for('open_folder', folder_name=folder_name))


@app.route('/download-file/<folder_name>/<filename>')
def download_file(folder_name, filename):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    file_path = os.path.join(user_folder, folder_name, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('File not found')
        return redirect(url_for('open_folder', folder_name=folder_name))


@app.route('/delete-account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        # flash('Please log in')
        return redirect(url_for('login'))
    
    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    
    # Delete all files in the user's folder
    if os.path.exists(user_folder):
        for file_name in os.listdir(user_folder):
            file_path = os.path.join(user_folder, file_name)
            os.remove(file_path)
        os.rmdir(user_folder)
    
    # Delete the user from the database
    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()
    
    session.pop('username', None)
    # flash('Account deleted successfully')
    return redirect(url_for('index'))


@app.route('/download-file/<folder_name>/<subfolder_name>/<filename>')
def download_subfile(folder_name, subfolder_name, filename):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    file_path = os.path.join(user_folder, folder_name, subfolder_name, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('File not found')
        return redirect(url_for('open_subfolder', folder_name=folder_name, subfolder_name=subfolder_name))

@app.route('/delete-file/<folder_name>/<subfolder_name>/<filename>')
def delete_subfile(folder_name, subfolder_name, filename):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    file_path = os.path.join(user_folder, folder_name, subfolder_name, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully')
    else:
        flash('File not found')

    return redirect(url_for('open_subfolder', folder_name=folder_name, subfolder_name=subfolder_name))

@app.route('/delete-subfolder/<folder_name>/<subfolder_name>')
def delete_subfolder(folder_name, subfolder_name):
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    folder_path = os.path.join(user_folder, folder_name, subfolder_name)

    if not os.path.exists(folder_path):
        flash('Subfolder not found')
        return redirect(url_for('open_subfolder', folder_name=folder_name, subfolder_name=subfolder_name))

    shutil.rmtree(folder_path)

    flash('Subfolder deleted successfully')
    return redirect(url_for('open_subfolder', folder_name=folder_name, subfolder_name=subfolder_name))


if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
    initialize_database()
    # app.run(debug=True)
    app.run(debug=True, host='0.0.0.0', port=2000)
    # app.run(host='0.0.0.0', port=2000)
