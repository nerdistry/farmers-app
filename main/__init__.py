from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager
from itsdangerous import TimedSerializer, URLSafeTimedSerializer 
from flask_uploads import IMAGES, UploadSet, configure_uploads
import os

# from werkzeug.utils import secure_filename


from werkzeug.utils import secure_filename  # Import secure_filename from werkzeug.utils


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/agrisense'

app.config.from_pyfile('../config.cfg')
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/products_images')
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static/Products_images'))

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'agrisensegenzai@gmail.com'
app.config['MAIL_PASSWORD'] = 'ffin tbmk hmul fyth'
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

from main import routes
