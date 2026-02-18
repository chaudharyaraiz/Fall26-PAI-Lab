from flask import Flask, jsonify
import requests

app = Flask(__name__)

# NASA Free API Key (You can use DEMO_KEY for testing)
API_KEY = "DEMO_KEY"
NASA_URL = "https://api.nasa.gov/planetary/apod"

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to NASA App Araiz",
        "endpoint": "/apod"
    })

@app.route('/apod', methods=['GET'])
def get_apod():
    try:
        response = requests.get(NASA_URL, params={"api_key": API_KEY})
        data = response.json()

        result = {
            "title": data.get("title"),
            "date": data.get("date"),
            "explanation": data.get("explanation"),
            "image_url": data.get("url")
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
