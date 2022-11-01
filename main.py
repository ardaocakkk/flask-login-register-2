from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bcrypt import Bcrypt


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'thisisasecretkey'
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CREATE TABLE IN DB
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 


with app.app_context():
    db.create_all()


class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email"})
    name = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Name"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Password"} )
    submit = SubmitField()
    



class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Password"} )
    submit = SubmitField()

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    
    
    
    
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, name=form.name.data,  password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        
        
        return redirect(url_for('login'))
    
            
    
    
    return render_template("register.html", form=form)


@app.route('/login',  methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('secrets'))
            if not bcrypt.check_password_hash(user.password, form.password.data):
                flash("That email or password does not exist, please try again.")
                return redirect(url_for('login'))
        if not user:
            flash("That email or password does not exist, please try again.")
            return redirect(url_for('login'))
    
    return render_template("login.html", form=form)


@app.route('/secrets' , methods = ["GET", "POST"])
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html", username=current_user.name )


@app.route('/logout', methods=["GET","POST"])
@login_required    
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/download')
def download():
    pass


if __name__ == "__main__":
    app.run(debug=True)
