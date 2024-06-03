from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'event_manager.db'

# Database setup and initialization
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        db = get_db()
        with app.app_context():
            db.executescript('''
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL
            );

            CREATE TABLE registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events (id)
            );

            INSERT INTO events (title, description, date) VALUES 
            ('Event 1', 'Description for Event 1', '2024-06-01'),
            ('Event 2', 'Description for Event 2', '2024-06-15'),
            ('Event 3', 'Description for Event 3', '2024-07-01');

            INSERT INTO registrations (event_id, user_name) VALUES 
            (1, 'Alice'),
            (2, 'Bob'),
            (3, 'Charlie'),
            (1, 'Dave');
            ''')
            db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')

# User management setup
event_managers = {
    "manager1": "password1",
    "manager2": "password2"
}

users = {
    "Unnathi": "Unnathi",
    "Sunitha": "Sunitha",
    "Shwetha": "Shwetha",
    "Vaishnavi": "Vaishnavi"
}

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in event_managers and event_managers[username] == password:
            session['username'] = username
            session['role'] = 'manager'
            return redirect(url_for('dashboard_manager', username=username))
        elif username in users and users[username] == password:
            session['username'] = username
            session['role'] = 'user'
            return redirect(url_for('dashboard_user', username=username))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/dashboard/manager/<username>')
def dashboard_manager(username):
    if 'username' in session and session['role'] == 'manager':
        return render_template('manage_events.html', username=username, role='manager1')
    return redirect(url_for('login'))

@app.route('/dashboard/user/<username>')
def dashboard_user(username):
    if 'username' in session and session['role'] == 'user':
        return render_template('ongoing.html', username=username, role='user')
    return redirect(url_for('login'))

@app.route('/interests')
def interests():
    return render_template('interest.html')

@app.route('/interests_1')
def interests_1():
    return render_template('interests_1.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/clubs')
def clubs():
    return render_template('clubs.html')

@app.route('/review')
def review():
    return render_template('review.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/events')
def show_events():
    db = get_db()
    cur = db.execute('SELECT id, title, description, date FROM events')
    events = cur.fetchall()
    return render_template('events.html', events=events)

@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register(event_id):
    if request.method == 'POST':
        user_name = request.form['user_name']
        db = get_db()
        db.execute('INSERT INTO registrations (event_id, user_name) VALUES (?, ?)',
                   [event_id, user_name])
        db.commit()
        flash('You have successfully registered for the event.')
        return redirect(url_for('show_events'))
    return render_template('register.html', event_id=event_id)

@app.route('/manage', methods=['GET', 'POST'])
def manage_events():
    if 'username' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        db.execute('INSERT INTO events (title, description, date) VALUES (?, ?, ?)',
                   [title, description, date])
        db.commit()
        flash('Event created successfully.')
    cur = db.execute('SELECT id, title, description, date FROM events')
    events = cur.fetchall()
    return render_template('manage_events.html', events=events)

@app.route('/update_event/<int:event_id>', methods=['GET', 'POST'])
def update_event(event_id):
    if 'username' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        db.execute('UPDATE events SET title = ?, description = ?, date = ? WHERE id = ?',
                   [title, description, date, event_id])
        db.commit()
        flash('Event updated successfully.')
        return redirect(url_for('manage_events'))
    cur = db.execute('SELECT id, title, description, date FROM events WHERE id = ?', [event_id])
    event = cur.fetchone()
    return render_template('update_event.html', event=event)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if 'username' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    db = get_db()
    db.execute('DELETE FROM events WHERE id = ?', [event_id])
    db.commit()
    flash('Event deleted successfully.')
    return redirect(url_for('manage_events'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
