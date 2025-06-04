from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))  # 'admin' or 'user'

class DataEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    datum = db.Column(db.Date)
    wert = db.Column(db.Float)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username']).first()
    if user and check_password_hash(user.password, request.form['password']):
        login_user(user)
        return redirect(url_for('dashboard'))
    return 'Login fehlgeschlagen'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        datum_str = request.form.get('datum')
        wert_str = request.form.get('wert')

        if datum_str and wert_str:
            try:
                datum = datetime.datetime.strptime(datum_str, '%Y-%m-%d').date()
                wert = float(wert_str)

                new_entry = DataEntry(user_id=current_user.id, datum=datum, wert=wert)
                db.session.add(new_entry)
                db.session.commit()
            except ValueError:
                # Fehlerhafte Eingabe
                return "Ungültiges Datum oder Wert", 400

        return redirect(url_for('dashboard'))

    # Daten des aktuellen Nutzers aus der DB holen
    entries = DataEntry.query.filter_by(user_id=current_user.id).all()

    return render_template('dashboard.html', current_user=current_user, entries=entries)

if __name__ == "__main__":
    app.run(debug=True)
