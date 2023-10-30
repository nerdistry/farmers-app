[AgriSense Logo](\main\static\assets\agri.png)

#  **AgriSense**


**Welcome to AgriSense!** AgriSense is designed to provide farmers with detailed responses, using Generative AI, based on their location. Our system identifies a user's location through an API, which is then passed on to weather and soil APIs as this information is crucial for farmers. By leveraging Generative AI, and incorporating methods such as langchain for embedding, our system provides detailed and accurate farming solutions.

Additionally, we have an integrated WhatsApp bot, capable of handling both images and text. This bot has been trained on the PlantVillage dataset using transfer learning (ResNet). More information on this feature can be found in its dedicated repository.

## **Purpose of AgriSense**

AgriSense aims to address the challenges faced by farmers by providing accurate and location-specific farming solutions using the power of Generative AI.

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

