# Live-Streaming-using-OpenCV-Flask
A Flask Web-App to stream live from local webcam or CCTV (rtsp link)

## Use Built-in Webcam of Laptop

### Put Zero (O) in cv2.VideoCapture(0)

``` cv2.VideoCapture(0) ```

### Use Ip Camera/CCTV/RTSP Link
``` cv2.VideoCapture('rtsp://username:password@camera_ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp')  ```

### Example RTSP Link
``` cv2.VideoCapture('rtsp://mamun:123456@101.134.16.117:554/user=mamun_password=123456_channel=0_stream=0.sdp') ```

### Change Channel Number to Change the Camera
``` cv2.VideoCapture('rtsp://mamun:123456@101.134.16.117:554/user=mamun_password=123456_channel=1_stream=0.sdp') ```

### Display the resulting frame in browser
``` cv2.imencode('.jpg', frame)[1].tobytes() ```

### Or this one
```
net , buffer = cv2.imencode('.jpg', frame)
buffer.tobytes()              
```

### [Reference](https://blog.miguelgrinberg.com/post/video-streaming-with-flask)



## to build .py script to exe using pyinstaller

1. first create a spec file and exclude the PyQt5 module

    ``pyi-makespec app.py --exclude-module PyQt5``

2. edit the spec file
            a = Analysis(
                ['app.py'],
                pathex=[],
                binaries=[],
                datas=[('shape_predictor_68_face_landmarks.dat','./face_recognition_models/models'),('shape_predictor_5_face_landmarks.dat','./face_recognition_models/models'),('mmod_human_face_detector.dat','./face_recognition_models/models'),('dlib_face_recognition_resnet_model_v1.dat','./face_recognition_models/models')],
                hiddenimports=[],
                hookspath=[],
                hooksconfig={},
                runtime_hooks=[],
                excludes=['PyQt5'],
                win_no_prefer_redirects=False,
                win_private_assemblies=False,
                cipher=block_cipher,
                noarchive=False,
            )

3. then copy the model .dat from python path to your project folder

4. then build the spec file

    ``` pyinstaller app.spec ```


5. then copy the `ImagesTrain`, `static` and `template` folder from folder project to result folder from pyinstaller in `dist/app`