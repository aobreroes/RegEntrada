

from flask import Flask, Blueprint, render_template, redirect, request, flash, url_for
from flask_login import login_required, LoginManager, current_user, login_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
import secrets
import crypt

app = Flask(__name__)

db = SQLAlchemy(app)
secret = secrets.token_urlsafe(32)
app.config['SECRET_KEY'] = secret

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///regdb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    is_admin = db.Column(db.Boolean, default=False)

class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100))
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user = db.Column(db.String(1000), nullable=False)


@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    names = db.session.query(User).all()
    return render_template("index.html", users=names)

@app.route('/', methods=['POST'])
@app.route('/index', methods=['POST'])
@app.route('/home', methods=['POST'])
def login_post():
    _name = request.form.get('name')
    _password = request.form.get('password')
    encryptpass = crypt.crypt(_password,'salt')

    user = User.query.filter_by(name=_name).first()

    if not user or encryptpass != user.password:
        flash('Datos incorrectos. Vuelve a intentarlo')
        return redirect(url_for('home'))

    login_user(user, remember=False)
    return redirect(url_for('profile'))

@app.route('/profile')
@login_required
def profile():

    users = User.query.all()
    registers = Action.query.all()
    status_now = Action.query.filter_by(user=current_user.name).order_by(Action.id.desc()).first()

    return render_template("profile.html", user=current_user, status_now=status_now, registers=registers, users=users)

@app.route('/logout', methods=['POST'])
@login_required
def action():

    status = None
    if request.form.get('entrada') == 'ENTRADA':
        status = "ENTRADA"
    elif request.form.get('descanso') == 'DESCANSO':
        status = "DESCANSO"
    elif request.form.get('salida') == 'SALIDA':
        status = "SALIDA"

    new_action = Action(status=status, user=current_user.name)
    db.session.add(new_action)
    db.session.commit()

    logout_user()
    return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user
    return redirect(url_for('home'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=True)
