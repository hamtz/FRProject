from django.shortcuts import redirect
# from flask import Flask, render_template, Response, url_for
# import os

import face_recognition
from flask import Flask, redirect, url_for, render_template, request, flash, Response, send_from_directory
import cv2
import numpy as np

from werkzeug.utils import secure_filename

import datetime
import time
import calendar

import threading

import pyrebase

import os.path

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# app = Flask(__name__)
app = Flask(__name__, template_folder='templates')  # still relative to module

# camera = cv2.VideoCapture('rtsp://freja.hiof.no:1935/rtplive/_definst_/hessdalen03.stream')  # use 0 for web camera
# camera = cv2.VideoCapture('http://192.168.43.31:81/stream')  # esp 32cam
camera = cv2.VideoCapture(1)  # use 0 for web camera

#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)


firebaseConfig = {"apiKey": "AIzaSyAKT2QoArXJFwoad4se-zjox44Y0AhmG2U", "authDomain": "realtimefr-e7201.firebaseapp.com",
                  "databaseURL": "https://realtimefr-e7201-default-rtdb.firebaseio.com/",
                  "projectId": "realtimefr-e7201", "storageBucket": "realtimefr-e7201.appspot.com",
                  "messagingSenderId": "440928093275", "appId": "1:440928093275:web:61759a7218fc6610376b7e",
                  "measurementId": "G-ESQJBD9MSG"}

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

path = 'ImagesTrain'
# path = r"C:\Users\Riku\Documents\Titip\Ilham\Kuliax\App\FR\ImagesTrain"
images = []
classNames = []
myList = os.listdir(path)
print(myList)
UPLOAD_FOLDER = 'ImagesTrain'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# @app.route('/encodeCurrImage', methods=['GET', 'POST'])
# def encodeCurrImage():

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
    data = classNames
    db.child("classNames").set(data)
print(classNames)
    # return redirect('/')

# encodeCurrImage()

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
        # db.child("encodeList").push(encodeList)

    return encodeList


encodeListKnown = findEncodings(images)
# db.child("encodeList").push(encodeListKnown)

print('Encoding Complete')


def tesdetect(name):
    # current_GMT = time.gmtime()
    # time_stamp = calendar.timegm(current_GMT)
    #
    # # KONVERSI HARI KE EPOCH TIME
    # today = datetime.date.today()
    # thisday = time.mktime(today.timetuple())
    # hari = int(thisday)
    #
    # data = {"name": name, "time": time_stamp,"day":hari}

    print(name)
    pass


# set upload to firebase untuk realtime


def setlistName(name):
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)

    # KONVERSI HARI KE EPOCH TIME
    today = datetime.date.today()
    thisday = time.mktime(today.timetuple())
    hari = int(thisday)

    data = {"name": name, "time": time_stamp}
    # db.push(data)
    db.child("detected").set(data)
    print(name)
    pass


# push upload to firebase untuk log history
def pushlistName(name):
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)

    # KONVERSI HARI KE EPOCH TIME
    today = datetime.date.today()
    thisday = time.mktime(today.timetuple())
    hari = int(thisday)

    data = {"name": name, "time": time_stamp, "day": hari}
    # db.push(data)
    db.child("history").push(data)
    pass


def genFrames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            # imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            # rgbImgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            rgbImgS = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


            facesCurFrame = face_recognition.face_locations(rgbImgS)
            encodesCurFrame = face_recognition.face_encodings(rgbImgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                # name = "Unknown"
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                print(faceDis)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    # print(name)

                    y1, x2, y2, x1 = faceLoc
                    # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4 //jika img diperkecil
                    y1, x2, y2, x1 = y1, x2, y2, x1
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    # cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                    setlistName(name)
                    pushlistName(name)  # tesdetect(name)
                else:
                    name = "Unknown"
                    y1, x2, y2, x1 = faceLoc
                    # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4 //jika img diperkecil
                    y1, x2, y2, x1 = y1, x2, y2, x1
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # print(name)
                    setlistName(name)
                    pushlistName(name)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
#
# @app.route('/restart', methods=['GET', 'POST'])
# def restart():
#     # encodeCurrImage()
#     # print(classNames)
#     # home_dir = os.system("cd ~")
#     # print("`cd ~` ran with exit code %d" % home_dir)
#     os.startfile("app.py")
#     return redirect('/')


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# // home
def generate_report():
    return "generating report"


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template("index.html")


@app.route('/histori')
def history():
    """HISTORY detect."""
    return render_template("history.html")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# GAGAL==================================================================
@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# GAGAL============================================================
# @app.route('/upload_image', methods=['POST'])
# def upload_image():
#     if 'file' not in request.files:
#         flash('No file part')
#         return redirect(request.url)
#     file = request.files['file']
#     if file.filename == '':
#         flash('No image selected for uploading')
#         return redirect(request.url)
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         print('upload_image filename: ' + filename)
#         flash('Image successfully uploaded and displayed below')
#         return render_template('upload.html', filename=filename)
#     else:
#         flash('Allowed image types are -> png, jpg, jpeg, gif')
#         return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
