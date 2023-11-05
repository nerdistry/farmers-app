import os, openai, io, base64, requests
from markupsafe import Markup
import secrets
import tempfile
from requests.auth import HTTPBasicAuth
from PIL import Image
from flask import jsonify, render_template, sessions, url_for, flash, redirect, request, session
from itsdangerous import BadSignature, Serializer, TimedSerializer, URLSafeTimedSerializer
from yaml import serialize_all 
from main import app, db, bcrypt, mail, photos
from main.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, BlogPostForm, AddProductsForm
from main.models import BlogPost, Category, Conversation, User, Product, Cart
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message, Mail
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from PIL import Image
from base64 import b64decode
from io import BytesIO
from dotenv import load_dotenv



@app.route("/")
@app.route("/home")
def home():
    active_page = 'home'
    response = requests.get('http://ip-api.com/json/')

    if response.status_code != 200:
        return 'Could not get location information.'

    location_data = response.json()
    session['location'] = location_data

    lat = location_data.get('lat')
    lon = location_data.get('lon')

#fetching weather data.
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric'
    response = requests.get(weather_url)

    if response.status_code != 200:
        return 'Could not get weather information.'

    weather_data = response.json()
    
    messages = [{'role':'user', 'content':f'based on this info write a short sentence that defines the weather for today \n {weather_data}'}]
    
    response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )

        # Extract the assistant's response
    response = response['choices'][0]['message']['content']
    items = 0
    if current_user.is_authenticated:
        user_id=current_user.id
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        items = len(cart_items)

        return render_template('home.html', active_page=active_page, response=response, items=items)
    
    return render_template('home.html', active_page=active_page, response=response)

@app.route("/about")
def about():
    user_id=current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    items = len(cart_items)
    active_page = 'about'
    return render_template('about.html', title='about', active_page=active_page, items=items)


mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.route("/registration", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, phone=form.phone.data, farm=form.farm.data, typeoffarming=form.typeoffarming.data)

        # Generate a confirmation token
        token = serializer.dumps(user.email, salt='email-confirm')

        # Send confirmation email
        confirmation_link = url_for('confirm_email', token=token, _external=True)
        message = Message('Confirm Your Email', recipients=[user.email], sender=app.config['MAIL_USERNAME'])
        message.body = f'Please click the link to confirm your email: {confirmation_link}'
        mail.send(message)

        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. Please check your email to confirm your account.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registration', form=form)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=1800)

        user = User.query.filter_by(email=email).first()
        if user:
            user.confirmed = True
            user.is_active = True
            db.session.commit()
            flash('Email confirmed. You can now log in.', 'success')
        else:
            flash('User not found.', 'danger')

    except BadSignature:
        flash('The confirmation link is invalid or has expired.', 'danger')

    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.confirmed:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Please confirm your email address to log in.', 'warning')
        else:
            flash('Login Unsuccessful. Please check email or password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profilepics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    active_page = 'profile'
    user_id=current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    items = len(cart_items)
    form= UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Account Updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
    image_file = url_for('static', filename='profilepics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, active_page=active_page, items=items)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='mylesadebayo@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

 
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


'''WEATHER AND SOIL APIs'''
@app.route('/weather&soil')
@login_required
def weatherandsoil():
    active_page = 'weatherandsoil'
    user_id=current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    items = len(cart_items)
    response = requests.get('http://ip-api.com/json/')

    if response.status_code != 200:
        return 'Could not get location information.'

    location_data = response.json()
    session['location'] = location_data
    print(location_data)

    lat = location_data.get('lat')
    lon = location_data.get('lon')

#fetching weather data.
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric'
    response = requests.get(weather_url)

    if response.status_code != 200:
        return 'Could not get weather information.'

    weather_data = response.json()
    print(weather_data)  # Print out the data to understand the structure

    # fetching soil data.
    AMBEEDATA_API_KEY = os.getenv('AMBEEDATA_API_KEY')
    soil_url = f'https://api.ambeedata.com/latest/by-lat-lng?lat={lat}&lng={lon}'
    headers = {"x-api-key": AMBEEDATA_API_KEY}
    response = requests.get(soil_url, headers=headers)
    print("Soil API Response: ", response.text)  # Add this line to print the response.

    if response.status_code != 200:
        return 'Could not get soil information.'
    else:
        soil_data = response.json()
        print(soil_data)
    return render_template('weatherandsoil.html', weather_data=weather_data, soil_data=soil_data, active_page=active_page)

from sqlalchemy import desc  # Import desc for descending order

@app.route("/viewposts", methods=['GET', 'POST'])
@login_required
def viewposts():
    active_page = 'viewposts'
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    items = len(cart_items)
    
    # Query blog posts in descending order of their creation date
    blogpost = BlogPost.query.order_by(desc(BlogPost.date_posted)).all()
    
    form = BlogPostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        post = BlogPost(title=title, content=content, user=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Blog posted successfully!', 'success')
        return redirect(url_for('viewposts'))
    
    return render_template('viewposts.html', blogpost=blogpost, form=form, active_page=active_page, items=items)


@app.route('/marketplace')
def marketplace():
    active_page = 'market_place'
    return render_template('marketplace.html', active_page=active_page)

@app.route('/help')
def help():
    active_page = 'help'
    return render_template('help.html', active_page=active_page)

@app.route('/profile')
def profile():
    active_page = 'profile'
    return render_template('profile.html', active_page=active_page)



'''
WORKING WITH API
'''
load_dotenv()
app.secret_key = os.getenv('APPSECRET_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPEN_API_KEY = os.getenv('OPENAI_KEY')
openai.api_key = OPEN_API_KEY
hf_api_key = os.getenv('HF_API_KEY')

'''
1. OPENAI API
'''
base_url = "https://api.openai.com/v1/"


'''Image Model DallE'''
def dalle_image(prompt, size):

    data = {
        "prompt": prompt,
        "size": size,
        'response_format': 'b64_json',
    }

    # download and transform the image
    response = requests.post(
        base_url + '/images/generations',
        headers={'Authorization': f'Bearer {OPEN_API_KEY}'},
        json=data
    )
    b64_image_data = response.json().get('data', [])[0].get('b64_json', '')

    decoded_image = base64.b64decode(b64_image_data)
    image = Image.open(BytesIO(decoded_image))

    return image

'''Image Model with Stable Diffusion'''

def stablediffusion_image(hf_api_key, text):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {hf_api_key}"}

    data = {"inputs": text}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        # Check if the response contains image data
        if 'image' in response.headers.get('Content-Type', '').lower():
            # Convert the response content to a Pillow image
            image = Image.open(BytesIO(response.content))
            
            # Resize the image to 256x256
            image = image.resize((256, 256))

            # You can save the resized image to a file if needed
            # image.save("resized_image.png")

            # Convert the Pillow image back to bytes
            resized_image_bytes = BytesIO()
            image.save(resized_image_bytes, format='PNG')
            return resized_image_bytes.getvalue()

    except Exception as e:
        print("Error occurred:", e)

    return None

'''ChatCompletion Model'''
model = 'gpt-3.5-turbo-16k'
@app.route('/farminginfo', methods=['GET', 'POST'])
def farminginfo():
    active_page = 'farminginfo'
    user_id=current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    items = len(cart_items)
    response = requests.get('http://ip-api.com/json/')

    if response.status_code != 200:
        return 'Could not get location information.'

    location_data = response.json()
    session['location'] = location_data

    lat = location_data.get('lat')
    lon = location_data.get('lon')

#fetching weather data.
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric'
    response = requests.get(weather_url)

    if response.status_code != 200:
        return 'Could not get weather information.'

    weather_data = response.json()
    #print(weather_data)  # Print out the data to understand the structure

  #fetching soil data.
    AMBEEDATA_API_KEY=os.getenv('AMBEEDATA_API_KEY')
    soil_url = f'https://api.ambeedata.com/latest/by-lat-lng?lat={lat}&lng={lon}'
    headers = {"x-api-key": AMBEEDATA_API_KEY}
    response = requests.get(soil_url, headers=headers)
    #print("Soil API Response: ", response.text)  # Add this line to print the response.

    if response.status_code != 200:
        return 'Could not get soil information.'
    else:
        soil_data = response.json()
        #print(soil_data )
    
    #form = FarmingInfoForm()

    if request.method == 'POST':
        system_message = "You are a farming expert to help in farming queries only. You speak in simple english that is easy to understand."
        user_message = f"Based on this: {weather_data}, and: {soil_data}, recommend 4 crops to plant and give reasons why for each."
        chat_log = [{"role": "system", "content": system_message},{"role": "user", "content": user_message}]    

        # Send the message to the GPT-4 model
        response = openai.ChatCompletion.create(
            model=model,
            messages=chat_log
        )

        # Extract the assistant's response
        crops_suggestions = response['choices'][0]['message']['content']
        
        
        conversation = Conversation(user_id=current_user.id, system_message=system_message, user_message=user_message, assistant_response = crops_suggestions)
        db.session.add(conversation)
        db.session.commit()
        

        # Append the assistant's response to the chat log
        chat_log.append({"role": "assistant", "content": crops_suggestions})
        #chat_log.append(assistant_response)
        
        get_first_crop = f"give only the name of the first crop suggested, name only."
        response2 = openai.ChatCompletion.create(
            model=model,
            messages=chat_log + [{"role": "user", "content": get_first_crop}]
        )
        first_crop = response2['choices'][0]['message']['content']
        
        conversation = Conversation(user_id=current_user.id,system_message=system_message, user_message=get_first_crop, assistant_response = first_crop)
        db.session.add(conversation)
        db.session.commit()
        
        chat_log.append({"role": "assistant", "content": first_crop})
        
        get_second_crop = f"give only the name of the second crop suggested, name only."
        response3 = openai.ChatCompletion.create(
            model=model,
            messages=chat_log + [{"role": "user", "content": get_second_crop}]
        )
        second_crop = response3['choices'][0]['message']['content']
        
        conversation = Conversation(user_id=current_user.id,system_message=system_message, user_message=get_second_crop, assistant_response = second_crop)
        db.session.add(conversation)
        db.session.commit()
        
        chat_log.append({"role": "assistant", "content": second_crop})

     
        get_third_crop = f"give only the name of the third crop suggested, name only."
        response4 = openai.ChatCompletion.create(
            model=model,
            messages=chat_log + [{"role": "user", "content": get_third_crop}]
        )
        third_crop = response4['choices'][0]['message']['content']
        
        conversation = Conversation(user_id=current_user.id,system_message=system_message, user_message=get_third_crop, assistant_response = third_crop)
        db.session.add(conversation)
        db.session.commit()
        
        chat_log.append({"role": "assistant", "content": third_crop})
  
        
        get_fourth_crop = f"give only the name of the fourth crop suggested, name only."
        response5 = openai.ChatCompletion.create(
            model=model,
            messages=chat_log + [{"role": "user", "content": get_fourth_crop}]
        )
        fourth_crop = response5['choices'][0]['message']['content']
        
        conversation = Conversation(user_id=current_user.id,system_message=system_message, user_message=get_fourth_crop, assistant_response = fourth_crop)
        db.session.add(conversation)
        db.session.commit()
        
        chat_log.append({"role": "assistant", "content": fourth_crop})

        get_pest_control_advice ="for each one of the crops, what pests affect them and suggest two ways to protect ech of those crops? give a link of where i can buy some of the remedies"
        response6 = openai.ChatCompletion.create(
            model=model,
            messages=chat_log + [{"role": "user", "content": get_pest_control_advice}]
        )
        pest_control_advice = response6['choices'][0]['message']['content']
        
        conversation = Conversation(user_id=current_user.id,system_message=system_message, user_message=get_pest_control_advice, assistant_response = pest_control_advice)
        db.session.add(conversation)
        db.session.commit()
        
        chat_log.append({"role": "assistant", "content": pest_control_advice})
        
     

        image_data = None
        prompt = (
            f"Craft a detailed, high-resolution image of {first_crop}")

        if request.method == 'POST':
            image_bytes = stablediffusion_image(hf_api_key, prompt)

        if image_bytes:
            # Convert the image bytes to base64
            image_data = base64.b64encode(image_bytes).decode('utf-8')

        image2_data = None
        prompt = (f"Craft a detailed, high-resolution image of {second_crop} .")

        if request.method == 'POST':
            image2_bytes = stablediffusion_image(hf_api_key, prompt)

        if image2_bytes:
            # Convert the image bytes to base64
            image2_data = base64.b64encode(image2_bytes).decode('utf-8')

        image3_data = None
        prompt = (f"Craft a detailed, high-resolution image of {third_crop} ")

        if request.method == 'POST':
            image3_bytes = stablediffusion_image(hf_api_key, prompt)

        if image3_bytes:
            # Convert the image bytes to base64
            image3_data = base64.b64encode(image3_bytes).decode('utf-8')

        image4_data = None
        prompt = (f"Craft a detailed, high-resolution image of  {fourth_crop} ")

        if request.method == 'POST':
            image4_bytes = stablediffusion_image(hf_api_key, prompt)

        if image4_bytes:
            # Convert the image bytes to base64
            image4_data = base64.b64encode(image4_bytes).decode('utf-8')


        # Render the 'gpt.html' template with the form and response
        return render_template('farminginfo.html', title='farminginfo', assistant_response=crops_suggestions, pest_control_advice=pest_control_advice ,first_crop=first_crop, image_data=Markup(image_data), second_crop=second_crop, image2_data=Markup(image2_data),  third_crop=third_crop, image3_data=Markup(image3_data),  fourth_crop=fourth_crop, image4_data=Markup(image4_data))

    # Render the 'gpt.html' template with the form when the page is initially loaded
    return render_template('farminginfo.html', title='farminginfo', active_page=active_page, items=items)

'''TESTING THE APIs'''
# Route for the home page
@app.route('/openai', methods=['GET', 'POST'])
def dalle():
    image_data = None
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        size = request.form.get('size')
        image = dalle_image(prompt, size)
        
        # Convert the image to bytes and encode it in base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return render_template('openai.html', image_data=image_data) 

@app.route('/huggingface', methods=['GET', 'POST'])
def huggingface():
    image_data = None
    if request.method == 'POST':
        text = request.form.get('text')
        image_bytes = stablediffusion_image(hf_api_key, text)

        if image_bytes:
            # Convert the image bytes to base64
            image_data = base64.b64encode(image_bytes).decode('utf-8')

    return render_template('huggingface.html', image_data=Markup(image_data))

@app.route("/advisor")
def advisor():
    active_page = 'advisor'
    user_id=current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    items = len(cart_items)
    return render_template("chat.html", active_page=active_page, items=items)

@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    messages = [{"role": "system", "content": "you are a farming expert to help in farming queries"}, 
                {"role": "user", "content": msg}]
    response = get_Chat_response(msg)
    messages.append(response)
    return jsonify({"response": response})

def get_Chat_response(text):
    messages = [{"role": "system", "content": "you are a farming expert to help in farming queries"}, 
                {"role": "user", "content": text}]
    response = openai.ChatCompletion.create(
        model=model,
        messages = messages
    )
    messages.append(response)
    return response['choices'][0]['message']['content']

@app.route('/addcategory', methods=['GET','POST'])
def addcategory():
    user_id=current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    items = len(cart_items)
    if request.method=="POST":
        getcategory = request.form.get('category')
        category = Category(category=getcategory)
        db.session.add(category)
        db.session.commit()
        flash(f'The Category {getcategory} was added', 'success')
        return redirect(url_for('addcategory'))
    return render_template('addcategory.html', items=items)


import hashlib
from uuid import uuid4
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Define a function to generate a unique filename
def generate_hex_name(filename):
    extension = filename.rsplit('.', 1)[1]  # Get the file extension
    unique_filename = f"{uuid4()}.{extension}"
    return unique_filename

def resize(width, height, path):
    with Image.open(path) as img:
        width, height = 300, 300  # Set your desired dimensions
        img = img.resize((width, height))
        img.save(path)
    return img

@app.route('/addproduct', methods=['POST', 'GET'])
def addproduct():
    active_page="addproduct"
    user_id=current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    items = len(cart_items)
    category = Category.query.all()
    form = AddProductsForm(request.form)
    
    if request.method == "POST":
        
        name = form.name.data
        user_id = current_user.id
        price = form.price.data
        stock = form.stock.data
        description = form.description.data
        category = request.form.get('category')
        image_1 = request.files.get('image_1')
        image_2 = request.files.get('image_2')
        image_3 = request.files.get('image_3')
        
        
        if image_1 and allowed_file(image_1.filename):
            unique_filename_1 = generate_hex_name(image_1.filename)
            image_1.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(unique_filename_1)))
            image_1_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(unique_filename_1))
            with Image.open(image_1_path) as img:
                width, height = 300, 300  # Set your desired dimensions
                img = img.resize((width, height))
                img.save(image_1_path)
        else:
            unique_filename_1 = None  # Or some default image if none is provided

        if image_2 and allowed_file(image_2.filename):
            unique_filename_2 = generate_hex_name(image_2.filename)
            image_2.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(unique_filename_2)))
            image_2_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(unique_filename_2))
            with Image.open(image_2_path) as img:
                width, height = 300, 300  # Set your desired dimensions
                img = img.resize((width, height))
                img.save(image_2_path)
        else:
            unique_filename_2 = None

        if image_3 and allowed_file(image_3.filename):
            unique_filename_3 = generate_hex_name(image_3.filename)
            image_3.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(unique_filename_3)))
            image_3_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(unique_filename_3))
            with Image.open(image_3_path) as img:
                width, height = 300, 300  # Set your desired dimensions
                img = img.resize((width, height))
                img.save(image_3_path)
        else:
            unique_filename_3 = None

        addpro = Product(
            name=name,
            user_id=user_id,
            price=price,
            stock=stock,
            description=description,
            category_id=category,
            image_1=unique_filename_1,  # Store the unique filenames in the database
            image_2=unique_filename_2,
            image_3=unique_filename_3
        )
        db.session.add(addpro)
        db.session.commit()
        flash(f"The product {name} has been added to your database", 'success')
        return redirect(url_for('addproduct'))
    return render_template('addproduct.html', title="Add Product Page", form=form, category=category, items=items, active_page=active_page)


@app.route('/admin')
def admin():
    products = Product.query.all()
    return render_template('admin.html', title='Admin Page', products = products)


@app.route("/store")
def store():
    active_page="store"
    user_id=current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    items = len(cart_items)
    products = Product.query.filter(Product.stock > 0)
    return render_template("store.html", products = products, active_page = active_page,items=items)


@app.route('/product/<int:id>', methods=['GET','POST'])
def single_page(id):
    user_id=current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    items = len(cart_items)
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        flash('Product added to cart succesfully!', 'success')
        
    return render_template('single_page.html', product=product, items=items)



def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

@app.route('/cart')
def cart():
    user_id = current_user.id 
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    products = []
    items = len(cart_items)
    final_total = 0
    phone = current_user.phone
    for item in cart_items:
        product = Product.query.get(item.product_id)
        product.quantity = item.quantity
        final_total += product.price * product.quantity
        final_total = int(final_total)
        products.append(product)
        
    return render_template('cart.html', cart=products, final_total=final_total, items=items, phone=phone)

@app.route('/<int:product_id>/add_to_cart', methods=['POST','GET'])
def add_to_cart(product_id):
    if current_user.is_authenticated:
        user_id = current_user.id 
        cart_item = Cart.query.filter_by(product_id=product_id, user_id=user_id).first()
        if cart_item:
            cart_item.quantity += 1
            cart_item.saveToDB()
        else:
            cart = Cart(product_id=product_id, user_id=user_id, quantity=1)
            cart.saveToDB()
    else:
        flash('You need to log in to add items to your cart','danger')
        return redirect(url_for('login'))
    flash('Product added to cart succesfully!', 'success')
    return redirect(url_for('store'))

@app.route('/cart/<int:product_id>/remove', methods=["POST", "GET"])
def remove_from_cart(product_id):
    user_id = current_user.id
    cart_item = Cart.query.filter_by(product_id=product_id, user_id=user_id).first()

    if not cart_item:
        return redirect(url_for('cart'))

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.saveToDB()
    else:
        cart_item.deleteFromDB()

    return redirect(url_for('cart'))

@app.route('/cart/clear', methods=["POST", "GET"])
def clear_cart():
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    for cart_item in cart_items:
        cart_item.deleteFromDB()

    return redirect(url_for('cart'))

my_endpoint = "https://78ef-102-213-179-25.ngrok-free.app"
@app.route('/pay', methods=['POST','GET'])
def MpesaExpress():
    getAccesstoken()
    user_id = current_user.id 
    phone = current_user.phone
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    final_total = 0
    for item in cart_items:
        product = Product.query.get(item.product_id)
        product.quantity = item.quantity
        final_total += product.price * product.quantity
        final_total = int(final_total)


    endpoint='https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    access_token = getAccesstoken()
    headers = {'Authorization': 'Bearer %s' % access_token}
    Timestamp = datetime.now()
    times = Timestamp.strftime('%Y%m%d%H%M%S')
    password = '174379' + 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919' + times
    password = base64.b64encode(password.encode('utf-8')).decode('utf-8')

    data = {
        "BusinessShortCode": "174379",    
        "Password": password,    
        "Timestamp":times,    
        "TransactionType": "CustomerPayBillOnline",    
        "PartyA":phone,    
        "PartyB":"174379", 
        "PhoneNumber": phone,   
        "CallBackURL":my_endpoint + '/callback',    
        "AccountReference":"Agrisense",    
        "TransactionDesc":"HelloTest",
        "Amount": final_total  

    }
    res = requests.post(endpoint, json=data, headers=headers)
    res.json()    
    clear_cart()
    flash('Thank you for shopping with Agrisense! Your order is being processed.', 'success')
    return redirect(url_for('cart'))
        
    
@app.route('/callback', methods=['POST'])
def incoming():
    data = request.get_json()
    print(data)
    return "ok"

def getAccesstoken():
    consumer_key = 'MxDfkY05AO0RFqKYGnBhp1LBjCNjTMqY'
    consumer_secret = 'M5lcztAHirHGAf6X'
    endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = r.json()
    return data['access_token']
