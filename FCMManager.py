
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("C:/Users/Riku/Documents/Titip/Ilham/Kuliax/App/FR/realtimefr-e7201-firebase-adminsdk-l2vta-55238c5548.json")
firebase_admin.initialize_app(cred)

def sendPush(title,msg,registration_token,dataObject=None):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
        title = title,
        body = msg
        ),
        data = dataObject,
        tokens = registration_token,
    )

    response = messaging.send_multicast(message)
    print("Successfully sent message: ", response)


