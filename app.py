from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databse.db'

db = SQLAlchemy(app)

app.secret_key = 'secrete_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phonenumber = db.Column(db.Integer, unique=True)
    password = db.Column(db.String(100))

    def __init__(self, name, email, phonenumber, password):
        self.name = name
        self.email = email
        self.phonenumber = phonenumber
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurantName = db.Column(db.String(100), nullable=False)
    productName = db.Column(db.String(100), nullable=False)
    productImage = db.Column(db.LargeBinary)

    def __init__(self, restaurantName, productName, productImage):
        self.restaurantName = restaurantName
        self.productName = productName
        self.productImage = productImage


with app.app_context():
    db.create_all()

admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Product, db.session))

@app.route('/')
def index():
    return render_template('email_verify.html')

# @app.route('/register', methods=['GET', 'POST'])
# def toRegister():
#


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        password = request.form['password']

        new_user = User(name=name, email=email, phonenumber=phonenumber, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/index')
        else:
            return render_template('login.html', error = 'Invalid User')

    return render_template('login.html')

@app.route('/index', methods=['GET', 'POST'])
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('index.html', user=user)
    return redirect('/login')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        restaurantName = request.form['restaurantName']
        productName = request.form['productName']
        productImage = request.files['productImage'].read()

        new_product = Product(restaurantName=restaurantName, productName=productName, productImage=productImage)
        db.session.add(new_product)
        db.session.commit()
        return redirect('/add_product')

    return render_template('supplier.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)