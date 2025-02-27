from flask import Flask, render_template, request, jsonify
from response import getResponse
import requests
import logging
from urllib.parse import quote

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#from app import app


app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')

def bot_api_calling(name, rating, feedback, response, category, count):
    # Make API call here
    '''
    Onestars ="★"
    Twostars ="★★"
    Threestars ="★★★"
    Fourstars ="★★★★"
    Fivestars ="★★★★★"
    '''
    starsOnRating = ""
    if (rating == 1):
        starsOnRating = "*"
    elif(rating == 2):
        starsOnRating = "**"
    elif(rating == 3):
        starsOnRating = "***"
    elif(rating == 4):
        starsOnRating = "****"
    elif(rating == 5):
        starsOnRating = "*****"

    feedback = feedback.replace("&", "and")
    response = response.replace("&", "and")

    # Encode the text properly
    text = f"{starsOnRating} {category} [UserName: {name} Comment:{feedback} Response: {response}]"
    encoded_text = quote(text)

    # Construct API URL
    api_url = f"https://epbot.blinkitech.com/api/file/saveusertext?bot=14&text={encoded_text}&remaining={count}"

    # Send GET request (ignore SSL errors)
    response = requests.get(api_url, verify=False)

    #api_url = f"https://epbot.blinkitech.com/api/file/saveusertext?bot=14&text={starsOnRating} {category} [UserName: {name} Comment:{feedback} Response: {response}]&remaining={count}"

    #print(api_url)
    #api_url = f"https://epbot.blinkitech.com/api/file/saveusertext?bot=14&text={starsOnRating}"
    #response = requests.get(api_url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api', methods=['POST'])
def api():
    try:
        data = request.get_json()
        name = data['name']
        feedback = data['comment']
        #count = data['count']
        # Call your Python script function
        response = getResponse(name, feedback)
        print(response)
        

        #bot_api_calling(name, rating, feedback, response, category, count)
        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'error': str(e)})
    
if __name__ == '__main__':
    app.run(debug=True)