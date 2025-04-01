#Project Name: Wireless DATA accqusition System
# lab : EAL Application lab
# Date : 03-04-2024
# Code : python script
#Details:
#        Author : Thummalabavi Sankshay Reddy
#        Roll no:23AT61R04
#        ATDC department


import firebase_admin
from firebase_admin import credentials, db
import time
import random
import numpy as np
import joblib

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(r"C:\Users\SUMAN KUMAR PAL\Desktop\NPK_DETECTION_FINAL\fir-demo-22684-firebase-adminsdk-er67w-2e407deab9.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://fir-demo-22684-default-rtdb.firebaseio.com'
    })


if firebase_admin.get_app():
    print("Connected to Firebase Realtime Database")
else:
    print("Failed to connect to Firebase Realtime Database")


def predict_potassium(mean_value):
    filename = 'd_100.sav'  
    model = joblib.load(filename)

    data_for_prediction = np.array(mean_value).reshape(-1, 1)
    predicted_potassium = model.predict(data_for_prediction)
    
    return predicted_potassium



while True:

    StartData = db.reference('/Start/').get()
    Digital = StartData['Digital']
    status = StartData['Transmission']
    Name = StartData['Details']['Name']
    Num_of_samples = StartData['Details']['Number']
    time.sleep(1)

    while Digital and status == "Ongoing":
        s = time.time()
        StartData = db.reference('/Start/').get()

        Digital = StartData['Digital']
        status = StartData['Transmission']
        Name = StartData['Details']['Name']
        Num_of_samples = StartData['Details']['Number']
        
        print("-----------------XXXXXXXXXXXXXXXXXXX-------------------")
        print()
        print("Details of soil sample")
        print(f"Name of the sample : {Name}")
        print(f"Number of samples : {Num_of_samples}")

        f = 0

        while status == "Ongoing":
            StartData = db.reference('/Start/').get()
            status = StartData['Transmission']
            if f == 0:
                print("Ongoing Transmisson")
                f = 1

        if status == "Done":
            #print("enter the dragon")
            testData = db.reference('/testData/').get()
            print("           -----xxxxx-----             ")
            print("Test Data is of :", Name)
            for row in testData:
                print(row)

            new_path = f'/Userdata/{Name}/'
            db.reference(new_path).set(testData)


            potassium_mean = []

            for row in testData:
                potassium_mean.append(row[0])

            k = predict_potassium(np.mean(potassium_mean))

            print()
            print("--------DATA PROCESSING PART ----------")
            print()

            print(f"value of potassium is {k}")
            array = {0,0,k}

            resultpath = f'/results/{Name}/'
            db.reference(resultpath).set(array)
            print("N P K values are:")
            print(array)

            output = f'/output'
            db.reference(output).set(array)

            db.reference('/testData/').delete()
            e = time.time()

            print("Transmission Done check the database for sample values")
            print()

        print("total time is", e-s)
        time.sleep(1)
