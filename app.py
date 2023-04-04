import calendar
import datetime
import json
import os.path
import time

import cv2
import face_recognition
import numpy as np
import pyrebase as pyrebase
from PIL import Image
from flask import Flask, redirect, url_for, render_template, request, flash, Response, jsonify
from numpy import asarray
from werkzeug.utils import secure_filename

import FCMManager as fcm

# from flask import Flask, render_template, Response, url_for
# import os

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# app = Flask(__name__)
app = Flask(__name__, template_folder='templates', static_folder='assets')  # still relative to module

# camera = cv2.VideoCapture('rtsp://freja.hiof.no:1935/rtplive/_definst_/hessdalen03.stream')  # use 0 for web camera
# camera = cv2.VideoCapture('http://192.168.43.31:81/stream')  # esp 32cam
# camera = cv2.VideoCapture('rtsp://admin:admin123@192.168.1.108/cam/realmonitor?channel=1&subtype=1')  # cctv
# camera = cv2.VideoCapture('http://192.168.43.21:8080/?action=stream')
camera = cv2.VideoCapture(0)  # use 0 for web camera
#

#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

# token my security android app
tokens = [
    "eNIG8mXEQsOmbrpoM-ji2i:APA91bHojqQckrSaQTUaCU7-9lWHppm7uTDBZ1fwkOaMZLrg12JIBbG476qaI6gjyOI38l8NrcASgXsmJTwv4J7RQv-82MyJP1k3LsELpRKDbXIh3SgHxJ3nUKnOcKNVfO07rVjOM3vz"]

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
UPLOAD_FOLDER = 'ImagesTrain'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
print(myList)


# @app.route('/encodeCurrImage', methods=['GET', 'POST'])
def setClassNames():
    # images = []
    # classNames = []
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
        data = classNames
        db.child("classNames").set(data)
    print(classNames)
    # return redirect('/')


# @app.route('/findencodings', methods=['GET', 'POST'])
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
        # db.child("encodeList").push(encodeList)
    return encodeList


setClassNames()
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
    db.child("history").push(data)
    pass


def genFrames():  # generate frame by frame from camera
    #   session["status"] = "Tidak Ada"
    # cap = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            # rgbImg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_small_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_small_frame)
            # face_locations = face_recognition.face_locations(rgbImg)
            curframe_encoding = face_recognition.face_encodings(rgb_small_frame, face_locations)
            # curframe_encoding = face_recognition.face_encodings(rgbImg, face_locations)

            if len(face_locations) == 0:
                f = open("nama.json", "w")
                f.write('{"nama" : "-"}')
            else:
                for encodeface, facelocation in zip(curframe_encoding, face_locations):
                    results = face_recognition.compare_faces(encodeListKnown, encodeface)
                    distance = face_recognition.face_distance(encodeListKnown, encodeface)
                    print(distance)
                    # print(results)
                    match_index = np.argmin(distance)

                    if results[match_index]:
                        name = classNames[match_index].upper()
                        # remove after "_" from name
                        name = name.split("_")[0]
                        f = open("nama.json", "w")
                        f.write('{"nama" : "' + name + '"}')
                        y1, x2, y2, x1 = facelocation
                        # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        y1, x2, y2, x1 = y1 * 2, x2 * 2, y2 * 2, x1 * 2
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        setlistName(name)
                        # pushlistName(name)

                        # cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (216, 138, 0), cv2.FILLED)
                        # cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    else:
                        name = "Unknown"
                        f = open("nama.json", "w")
                        f.write('{"nama" : "Unknown"}')
                        setlistName(name)
                        # pushlistName(name)
                        y1, x2, y2, x1 = facelocation
                        # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        y1, x2, y2, x1 = y1 * 2, x2 * 2, y2 * 2, x1 * 2
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                        # cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (216, 138, 0), cv2.FILLED)
                        # cv2.putText(frame, "Unknown", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # return frame and the name
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/shutdown')
def shutdown():
    camera.release()
    # cv2.destroyAllWindows()
    return render_template("index.html")


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


# BERHASIL ==================================================================
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
        # if file and allowed_file(file.filename):
        if file:
            extfilename = secure_filename(file.filename).split('.', 1)[1].lower()
            # filename = secure_filename(request.form['filename'])
            filename = request.form['filename'] + '.' + extfilename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if True:
                print(filename)
                time.sleep(3)
                try:
                    pathFile= os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    curImg = cv2.imread(pathFile)

                    # Tentukan path ke file gambar
                    # name = str(filename)
                    # imgPath = os.path.join("ImagesTrain", name)
                    # img = Image.open(imgPath)
                    imgUp = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    imgNump = asarray(imgUp)
                    img = cv2.cvtColor(imgNump, cv2.COLOR_BGR2RGB)
                    # imgRead = cv2.imread(img)

                    faceEncodings = face_recognition.face_encodings(img)
                    if len(faceEncodings) > 0:
                        addEncode = faceEncodings[0]
                        encodeListKnown.append(addEncode)
                        if encodeListKnown:
                            if True:
                                images.append(curImg)
                                classNames.append(os.path.splitext(filename)[0])
                                data = classNames
                                db.child("classNames").set(data)
                                print(classNames)
                                print("Berhasil menambahkan.")
                            else:
                                print("Gagal menambahkan.")

                    else:
                        # images.remove(curImg)
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        print("Tidak ada wajah yang terdeteksi pada gambar.")
                        return render_template("upload_image.html")

                except Exception as e:
                    print(f"Error: {str(e)}")

                return redirect(url_for('index'))
            else:
                print("gagal upload file")
    return render_template("upload_image.html")


# @app.route('/uploads/<filename>')
# @app.route('/uploads')
# def upload_success():
# send_from_directory(app.config['UPLOAD_FOLDER'], filename)
# setClassNames()
# findEncodings(images)
#
# print("upload success")
# print(myList)
# return render_template("index.html")


@app.route('/pushnotif')
def pushnotif():
    with open("nama.json") as f:
        data = json.load(f)
        nama = data["nama"]
        if nama == "Unknown":
            fcm.sendPush("Warning", "An unknown person has detected", tokens)
            print("Unknown people detected")
        return jsonify(nama)


@app.route('/setname')
def setName():
    with open("nama.json") as f:
        data = json.load(f)
        nama = data["nama"]
        return jsonify(nama)


# @app.route('/pushname')
# def pushName():
#     with open("nama.json") as f:
#         data = json.load(f)
#         nama = data["nama"]
#         return jsonify(nama)

# def checkEncode():
#
#     curImg = cv2.imread(file.filename)
#     images.append(curImg)
#     classNames.append(os.path.splitext(filename)[0])
#     data = classNames
#     db.child("classNames").set(data)
#     print(classNames)
#
#     imgUp = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#     imgNump = asarray(imgUp)
#     img = cv2.cvtColor(imgNump, cv2.COLOR_BGR2RGB)
#     addEncode = face_recognition.face_encodings(img)[0]
#     encodeListKnown.append(addEncode)

if __name__ == '__main__':
    app.run(debug=True)
