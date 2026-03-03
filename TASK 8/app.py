from flask import Flask, render_template
import requests

app = Flask(__name__)

API_KEY = "K2G3ZfhVgrdZvtaW6AQ4mkqtFC1mKeZ0DnFed0x8"
NASA_URL = "https://api.nasa.gov/planetary/apod"

@app.route('/')
def home():
    try:
        response = requests.get(NASA_URL, params={
            "api_key": API_KEY,
            "thumbs": True
        })

        data = response.json()

        print("FULL DATA:", data)  # DEBUG

        media_type = data.get("media_type")

        # Default image URL logic
        if media_type == "image":
            url = data.get("hdurl") or data.get("url")

        elif media_type == "video":
            url = data.get("thumbnail_url")  # show thumbnail

        else:
            url = None

        return render_template("index.html", data={
            "title": data.get("title"),
            "date": data.get("date"),
            "explanation": data.get("explanation"),
            "url": url
        })

    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)