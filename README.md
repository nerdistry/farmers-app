<p align="center">
  <img src="main/static/pictures/agri-logo.png" alt="AgriSense Logo">
</p>
#  **AgriSense**

**Welcome to the AgriSense Repository!** 
AgriSense is a Generative AI-based solution that aims to provide farmers with expert advice on agriculture.
Our solution does this by fetching the farmer's geo-details, providing crop recommendations, crop farming plans, and a specialized chatbot available on the web and also via WhatsApp.
More information on these features can be found in the repository.

## **Purpose of AgriSense**

AgriSense aims to address farmers' challenges by providing precise and location-specific farming solutions powered by Generative AI. It uses APIs to determine the farmer's location and geo-details such as weather, soil, wind, humidity level, and so on. It feeds that data into our trained generative AI model, gpt-3.5-turbo, which generates images and short descriptions of recommended crops, as well as farming rotation plans to ensure the farm's success. It also contains information on pests and diseases that are likely to infest the farm if the recommended crops are planted, as well as resources for dealing with them. It has a web-based chatbot as well as a [WhatsApp](https://github.com/nerdistry/gpt_bot) chatbot powered by a pre-trained [model](https://github.com/nerdistry/plant-village-trained-model). It also fosters a sense of community by allowing farmers to comment and rate the effectiveness of the solution.

## **Structure**
The repository is structured as follows:  
Resources such as the CSS and images are located in the static folder.  
The web pages are located in the templates folder.  
The models are in the main folder which encompasses the bulk of the repository.  
The Whatsapp bot is located in this [repo](https://github.com/nerdistry/gpt_bot) and the model it is based on is located [here](https://github.com/nerdistry/plant-village-trained-model).

## **Tech Stack**
- [Flask](https://palletsprojects.com/p/flask/)
- [MySQL](https://www.mysql.com/downloads/)

To set up the environment, ensure you have Flask and MySQL installed. You can download and install them from their respective links.

## **How to Run AgriSense**

Before starting, you need to set up your `.env` file:

```markdown
APPSECRET_KEY = '<YOUR APP SECRET KEY>'
OPENWEATHER_API_KEY = '<YOUR OPEN WEATHER KEY>'
AMBEEDATA_API_KEY = '<YOUR AMBEEDATA KEY>'
OPENAI_KEY = '<YOUR OPEN AI KEY>'
HF_API_KEY = '<YOUR HUGGING FACE KEY>'
```
To obtain API keys, visit the following links, sign up and you will be good to go:
- [OpenWeather](https://home.openweathermap.org/users/sign_up)
- [AmbeeData](https://www.ambeedata.com/)
- [OpenAI](https://www.openai.com/)
- [HuggingFace](https://huggingface.co/)

Next, set up your database:
1. Ensure you have a database named 'agrisense' in your system.
2. Ensure XAMPP is running.

> Note: Tables will be automatically generated for you after running the application.

Install the required libraries:
```bash
pip install -r requirements.txt
```

Set up your virtual environment:

**Windows**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Ubuntu/Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

**MacOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

Finally, run the application:
```bash
python run.py
```

Additionally, update the contents of `.cfg` with your details:
```markdown
MAIL_SERVER = 'smtp.gmail.com'
MAIL_USERNAME = 'Your Username'
MAIL_PASSWORD = 'Your Password'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False
```

---

