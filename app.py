from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# Configure MySQL
app.secret_key = '07e2fbaf423a63c09297220ff63ff01495f900c6f04ff6f8'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'priyaa'
app.config['MYSQL_PASSWORD'] = 'sqlpass'
app.config['MYSQL_DB'] = 'social_media_app'

mysql = MySQL(app)

# Setup Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()

    if user_data:
        user_instance = User()
        user_instance.id = user_data[0]
        user_instance.username = user_data[3]  # Assuming the username is at index 3
        return user_instance

    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username_to_search = request.form['username']

        # Check if the username exists in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username_to_search,))
        user_data = cur.fetchone()
        cur.close()

        if user_data:
            # User found, redirect to their profile
            return redirect(url_for('profile', user_id=user_data[0]))
        else:
            # User not found, display a message
            return render_template('search_result.html', message="User not found")

    cur = mysql.connection.cursor()
    cur.execute("SELECT posts.content, users.username FROM posts JOIN users ON posts.user_id = users.id")
    posts = cur.fetchall()
    cur.close()

    user_info = {'username': current_user.username if current_user.is_authenticated else None}

    return render_template('index.html', posts=posts, user_info=user_info)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user_data = cur.fetchone()
        cur.close()

        if user_data:
            user = User()
            user.id = user_data[0]
            user.username = user_data[3]  # Assuming the username is at index 3
            login_user(user)
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    # Fetch all user information from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
    user_information = cur.fetchone()
    cur.close()

    # Create a dictionary to store user information
    user_profile = {
        'id': user_information[0],
        'name': user_information[1],
        'email': user_information[2],
        'username': user_information[3],
        # Add more profile information here as needed
    }

    return render_template('profile.html', user_profile=user_profile)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        # Handle post creation logic here
        post_content = request.form['post_content']

        # Insert the post into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO posts (user_id, content) VALUES (%s, %s)", (current_user.id, post_content))
        mysql.connection.commit()
        cur.close()

        # Redirect to the index page after creating the post
        return redirect(url_for('index'))

    return render_template('create_post.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)",
                    (name, email, username, password))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template('register.html')
@app.route('/search')
def search():
    # Get the username from the query parameters
    username_to_search = request.args.get('username')

    # Search for the user in the users table
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username_to_search,))
    user_data = cur.fetchone()
    cur.close()

    # Render the search_results.html template and pass the user_data
    return render_template('search_result.html', user_data=user_data)

    
if __name__ == '__main__':
    app.run(debug=True)
