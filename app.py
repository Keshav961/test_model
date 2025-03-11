from flask import Flask, request, jsonify
import pandas as pd
import base64
import openai
from fuzzywuzzy import process
from dotenv import load_dotenv
import os


app = Flask(__name__)
load_dotenv()
client = openai.OpenAI()


UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load car parts list
file_path = "594_Category - Sheet1.csv"
df = pd.read_csv(file_path)
car_parts_list = df.iloc[:, 0].dropna().tolist()


def classify_car_part(image_data: bytes):
    """Send image to ChatGPT and get the car part name."""
    base64_image = base64.b64encode(image_data).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
        {
            "role": "user",
            "content": [
                { "type": "text", "text": "You are an expert in identifying automotive car parts. Return only the part name, nothing else." },
                {"type":"text","text":"Identify this car part from the image."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
        }
    ],
    )
    predicted_part = response.choices[0].message.content.strip()
    return predicted_part


def find_best_match(part_name):
    """Find the best matching car part name from the 594-category list."""
    best_match, _ = process.extractOne(part_name, car_parts_list)
    return best_match


@app.route('/post-data', methods=['POST'])
def post_data():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        image_data = image_file.read()

        # Classify the car part
        predicted_part = classify_car_part(image_data)
        matched_part = find_best_match(predicted_part)
        
        # image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        # image_file.save(image_path)

        return jsonify({
            "name": matched_part
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8337, debug=True)
