import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)
import firebase_admin
from firebase_admin import credentials, db
import time
from parameters import *
import numpy as np
import tensorflow as tf


class FirebaseConnect:

    def __init__(self):
        self.cred_path =CRED_PATH
        self.db_url = URL
        self.initialize()

    def initialize(self):
        try:
            cred = credentials.Certificate(self.cred_path)
            firebase_admin.initialize_app(cred, {'databaseURL': self.db_url})
            print("✅ Successfully connected to Firebase Realtime Database")
        except Exception as e:
            print("❌ Failed to initialize Firebase connection.")
            print(f"Error: {e}")

class Initialize:

    def __init__(self):
        self.path = INITIALIZATION_PATH
        
        self.data = {
            'Sample_Name': 's',
            'Sample_Size': 1000,
            'Start':True,
            'Status':'Ongoing'
        }


    def set(self):
        db.reference(self.path).set(self.data)
        print(f"✅ Data set : {self.data}")


    def get(self):
        result = db.reference(self.path).get()
        if result:
            array = list(result.values())
            return array[0],array[1],array[2],array[3]
        
        else:
            return 0,0,0,0



def  collect_samples():

    details = Initialize()
    details.set()
    Sample_Name,Sample_Size,Start,Status = details.get()

    while Start == False:
        time.sleep(1)
        

    while Start and Status == "Ongoing":
        _, _, Start, Status = details.get()

        
    if Status == "Done":
        details.set()

        soil_data_path = f'/{SOIL_DATA_PATH}/{Sample_Name}/'

        tempdata = db.reference('/tempdata/').get()
        db.reference(soil_data_path).set(tempdata)
        db.reference('/tempData/').delete()




def NPK_computation():

    Sample_Name = 'sunshine'
    soil_data_path = f'/{SOIL_DATA_PATH}/{Sample_Name}/'
    resultpath = f'{RESULTS_PATH}/{Sample_Name}/'
    modelpath = f'{MODEL_PATH}/soil_prediction_model.h5'

    data = db.reference(soil_data_path).get()

    if data is None:
        print(f"❌ Sample name '{Sample_Name}' does not exist in {SOIL_DATA_PATH}.")
    else:

        print(f"✅ Sample name '{Sample_Name}' found. Proceeding with data...")

        data_array = np.array(data, dtype=float)

        input = np.mean(data_array, axis=0).reshape(1,-1)

        model = tf.keras.models.load_model(modelpath, custom_objects={'mse': tf.keras.losses.MeanSquaredError()})

        predictions = model.predict(input)

        predictions_list = [round(val, 3) for val in predictions[0].tolist()]

        print("Model Prediction [N P K]:", predictions_list)

        db.reference(resultpath).set(predictions_list)
        db.reference(OUTPUT_PATH).set(predictions_list)



if __name__ == "__main__":

    FirebaseConnect()
    #collect_samples()
    NPK_computation()

