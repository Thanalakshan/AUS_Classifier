from flask import Flask, request, jsonify, render_template
import joblib
import json
import numpy as np
import base64
import cv2
import pywt
import logging

app = Flask(__name__)

__class_name_to_number = {}
__class_number_to_name = {}
__model = None

def w2d(img, mode='haar', level=1):
    imArray = img
    imArray = cv2.cvtColor(imArray, cv2.COLOR_RGB2GRAY)
    imArray = np.float32(imArray)
    imArray /= 255
    coeffs = pywt.wavedec2(imArray, mode, level=level)
    coeffs_H = list(coeffs)
    coeffs_H[0] *= 0
    imArray_H = pywt.waverec2(coeffs_H, mode)
    imArray_H *= 255
    imArray_H = np.uint8(imArray_H)
    return imArray_H

def classify_image(image_base64_data, file_path=None):
    imgs = get_cropped_image_if_2_eyes(file_path, image_base64_data)
    if not imgs:
        return {'error': 'No face or not enough eyes detected'}

    predicted_players = []
    for img in imgs:
        scalled_raw_img = cv2.resize(img, (32, 32))
        img_har = w2d(img, 'db1', 5)
        scalled_img_har = cv2.resize(img_har, (32, 32))
        combined_img = np.vstack((scalled_raw_img.reshape(32 * 32 * 3, 1), scalled_img_har.reshape(32 * 32, 1)))

        len_image_array = 32 * 32 * 3 + 32 * 32

        final = combined_img.reshape(1, len_image_array).astype(float)
        try:
            class_prediction = __model.predict(final)[0]
            predicted_player = class_number_to_name(class_prediction)
            predicted_players.append(predicted_player)
        except IndexError as e:
            logging.exception("IndexError in classify_image: %s", str(e))
            return {'error': 'Model prediction error: ' + str(e)}

    return {'predicted_player': predicted_players}

def class_number_to_name(class_num):
    return __class_number_to_name.get(class_num, "Unknown")

def load_saved_artifacts():
    print("loading saved artifacts...start")
    global __class_name_to_number
    global __class_number_to_name

    with open("./class_dictionary.json", "r") as f:
        __class_name_to_number = json.load(f)
        __class_number_to_name = {v: k for k, v in __class_name_to_number.items()}

    global __model
    if __model is None:
        with open('./saved_model.pkl', 'rb') as f:
            __model = joblib.load(f)
    print("loading saved artifacts...done")

def get_cv2_image_from_base64_string(b64str):
    try:
        logging.info("Received base64 string: %s", b64str[:30])
        if ',' in b64str:
            encoded_data = b64str.split(',')[1]
        else:
            encoded_data = b64str

        if not encoded_data:
            logging.error("Empty base64 string received")
            return None

        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)

        if nparr.size == 0:
            logging.error("Empty numpy array received from base64 string")
            return None

        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            logging.error("Failed to decode image from base64 string")
            return None

        return img
    except Exception as e:
        logging.exception("Exception in get_cv2_image_from_base64_string: %s", str(e))
        return None

def get_cropped_image_if_2_eyes(image_path, image_base64_data):
    face_cascade = cv2.CascadeClassifier('./haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('./haarcascades/haarcascade_eye.xml')

    if image_path:
        img = cv2.imread(image_path)
    else:
        img = get_cv2_image_from_base64_string(image_base64_data)
        if img is None:
            return []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    cropped_faces = []
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) >= 2:
            cropped_faces.append(roi_color)
    return cropped_faces

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify_image', methods=['POST'])
def classify_image_endpoint():
    try:
        image_data = request.form['image_data']
        logging.info("Received image data: %s", image_data[:30])
        if not image_data:
            logging.error("Empty base64 string received")
            return jsonify({'error': 'Empty base64 string received'}), 400
        response = classify_image(image_data)
        return jsonify(response)
    except Exception as e:
        logging.exception("Error occurred during image classification")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_saved_artifacts()
    app.run(port=5000)