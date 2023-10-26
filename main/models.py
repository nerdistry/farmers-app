from datetime import datetime
from main import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedSerializer as Serializer



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    farm = db.Column(db.String(3), nullable=False)
    typeoffarming = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    blogpost = db.relationship('BlogPost', backref='user', lazy=True)
    confirmed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Override the is_active method
    def is_active(self):
        return self.confirmed

    def get_id(self):
        return str(self.id)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Blogpost('{self.title}', '{self.date_posted}')"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), nullable=False, unique=True)
    
class Addproduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('product_category', lazy=True))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    image_1 = db.Column(db.String(150), nullable =False, default='image.jpg')
    image_2 = db.Column(db.String(150), nullable =False, default='image.jpg')
    image_3 = db.Column(db.String(150), nullable =False, default='image.jpg')
    
    def __repr__(self):
        return '<Addproduct %r>' % self.name
    
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    system_message = db.Column(db.Text, nullable=True)
    user_message = db.Column(db.Text, nullable = False)
    assistant_response = db.Column(db.Text, nullable = True)
