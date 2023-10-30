from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, SelectField, FileField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Enter your username"})
    phone = StringField('Phone Number',
                           validators=[DataRequired(), Length(min=12, max=13)], render_kw={"placeholder": "i.e. 2547xxxxxxxx"})
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"})
    
    farm = SelectField('Do you have a farm?', choices=[('', ''),('yes', 'Yes'), ('no', 'No')], default='no')
    typeoffarming = SelectField('Type of Farming', choices=[('', ''),('domestic farming', 'Domestic Farming'), ('commercial farming', 'Commercial Farming'), ('sustainable farming', 'Sustainable Farming')], validators=[DataRequired()], render_kw={"placeholder": "Which type of farming do you want to do?"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Minimum: 8 characters"})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):

        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('This username is taken, please choose a different one')
        

    def validate_email(self, email):

        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('This Email is taken, please choose a different one')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number',validators=[DataRequired(), Length(min=12, max=13)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('This username is taken, please choose a different one')
        

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('This Email is taken, please choose a different one')
    
            

class RequestResetForm(FlaskForm):
        email = StringField('Email',
                        validators=[DataRequired(), Email()])
        submit = SubmitField('Request Password Reset')

        def validate_email(self, email):
            user = User.query.filter_by(email=email.data).first()
            if user is None:
                raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
    

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
    
class AddProductsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "Input the name of the product"})
    price= IntegerField('Price', validators=[DataRequired()], render_kw={"placeholder": "Input the price per kilogramme(kg)"})
    stock = IntegerField('Stock', validators=[DataRequired()], render_kw={"placeholder": "Input the stock in kilograms(kgs)"})
    description = TextAreaField('Description', validators=[DataRequired()], render_kw={"placeholder": "Input product Description"})
    
    image_1 = FileField('image_1', validators=[FileRequired('Image is required'), FileAllowed(['jpg', 'png', 'jpeg'], 'images only please')])
    image_2 = FileField('image_2', validators=[FileRequired('Image is required'), FileAllowed(['jpg', 'png', 'jpeg'], 'images only please')])
    image_3 = FileField('image_3', validators=[FileRequired('Image is required'), FileAllowed(['jpg', 'png', 'jpeg'], 'images only please')])