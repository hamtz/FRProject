# from datetime import datetime, date
import calendar
import datetime
import time

import pyrebase

firebaseConfig = {"apiKey": "AIzaSyAKT2QoArXJFwoad4se-zjox44Y0AhmG2U",
                  "authDomain": "realtimefr-e7201.firebaseapp.com",
                  "databaseURL": "https://realtimefr-e7201-default-rtdb.firebaseio.com/",
                  "projectId": "realtimefr-e7201",
                  "storageBucket": "realtimefr-e7201.appspot.com",
                  "messagingSenderId": "440928093275",
                  "appId": "1:440928093275:web:61759a7218fc6610376b7e",
                  "measurementId": "G-ESQJBD9MSG"
                  }

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

current_GMT = time.gmtime()
time_stamp = calendar.timegm(current_GMT)

today = datetime.date.today()
print("Today's date:", today)

# s = "2022-10-25"
# s = today
# converttime=time.mktime(datetime.datetime.strptime(s,"%Y-%m-%d").timetuple())
# print("Today's date convert time:", converttime)


# current date and time
current_GMT = time.gmtime()
time_stamp = calendar.timegm(current_GMT)
print("timestamp =", time_stamp)

# KONVERSI HARI KE EPOCH TIME
thisday=time.mktime(today.timetuple())
hari = int(thisday)
print("Today's date convert:", hari)


# push data
data = {"name": "Delta", "time": time_stamp,"day":hari}

db.child("log").push(data)

# logtime = db.child("log").child(thisday).get()

# for logs in logtime.each():
#     print(logs.val())



# db.child("log").child("2022-10-24").push(data)

# today = date.today()
# now = date.now()
#
# timestamp = date.timestamp(now)
# today = date.today()
#
# print("Today's date:", today)
# print("Today's date:", now)
# db.push(data)


#
# if today == date.today():
#   # db.push(data)
#
#   print("sama")
# else:
#     print("tidak sama")
