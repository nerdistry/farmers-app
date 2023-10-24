from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, SelectField, FileField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    farm = SelectField('Do you have a farm?', choices=[('', ''),('yes', 'Yes'), ('no', 'No')], default='no')
    typeoffarming = SelectField('Type of Farming', choices=[('', ''),('domestic farming', 'Domestic Farming'), ('commercial farming', 'Commercial Farming'), ('sustainable farming', 'Sustainable Farming')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
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


          
'''
class FarmingInfoForm(FlaskForm):
    q1 = SelectField('What is the average temperature range in your area during the growing season?',
                    choices=[
                        ('',''),
                        ('Below 10°C (Cold)', 'Below 10°C (Cold)'),
                        ('10-20°C (Cool)', '10-20°C (Cool)'),
                        ('20-30°C (Moderate)', '20-30°C (Moderate)'),
                        ('30-40°C (Warm)', '30-40°C (Warm)'),
                        ('Above 40°C (Hot)', 'Above 40°C (Hot)')
                    ])
    q2 = SelectField('How much rainfall does your region receive annually?',
                    choices=[
                        ('',''),
                        ('Less than 500 mm annually (Arid)', 'Less than 500 mm annually (Arid)'),
                        ('500-1000 mm annually (Semi-arid)', '500-1000 mm annually (Semi-arid)'),
                        ('1000-1500 mm annually (Sub-humid)', '1000-1500 mm annually (Sub-humid)'),
                        ('More than 1500 mm annually (Humid)', 'More than 1500 mm annually (Humid)')
                    ])
    q3 = SelectField('What crops were grown on your land in the previous season?',
                    choices=[
                        ('',''),
                        ('Corn (Maize)', 'Corn (Maize)'),
                        ('Rice', 'Rice'),
                        ('Wheat', 'Wheat'),
                        ('Potatoes', 'Potatoes'),
                        ('Tomatoes', 'Tomatoes'),
                        ('Onions', 'Onions'),
                        ('Beans', 'Beans')
                    ])
    q4 = SelectField('What crops are currently in high demand in your local market?',
                    choices=[
                        ('',''),
                        ('Corn (Maize)', 'Corn (Maize)'),
                        ('Rice', 'Rice'),
                        ('Wheat', 'Wheat'),
                        ('Potatoes', 'Potatoes'),
                        ('Tomatoes', 'Tomatoes'),
                        ('onions', 'Onions'),
                        ('Beans', 'Beans')
                    ])
    q5 = SelectField('Does your soil retain moisture well, or does it tend to dry out quickly?',
                    choices=[
                        ('',''),
                        ('Poor (Dries quickly)', 'Poor (Dries quickly)'),
                        ('Fair', 'Fair'),
                        ('Good (retains moisture well)', 'Good (Retains Moisture Well)')
                    ])
    q6 = SelectField('What is the altitude of your farming location?',
                    choices=[
                        ('',''),
                        ('Below 500 meters (Plain)', 'Below 500 meters (Plain)'),
                        ('500-1000 meters (Moderate)', '500-1000 meters (Moderate)'),
                        ('1000-1500 meters (Highland)', '1000-1500 meters (Highland)'),
                        ('1500-2000 meters (Mountainous)', '1500-2000 meters (Mountainous)'),
                        ('Above 2000 meters (High Alpine)', 'Above 2000 meters (High Alpine)')
                    ])
'''