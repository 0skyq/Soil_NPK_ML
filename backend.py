import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)
from parameters import *
import numpy as np
import tensorflow as tf
from tkinter import filedialog 
import csv

class Backend:

    def __init__(self, firebase_handler, process_handler):
        self.fb = firebase_handler
        self.process_handler = process_handler

    def set(self, data):
        self.fb.user_ref.set(data)
        print(f"✅ Data set : {data}")

    def get(self):
        result = self.fb.user_ref.get()
        if result:
            array = list(result.values())
            return array[0], array[1], array[2], array[3]
        else:
            return 0, 0, 0, 0


    def collect(self,data):
        self.set(data)
        Sample_Name, Sample_Size, Start, Status = self.get()
            
        print(f'Transmisson Status : {Status}')
        while Status == "Ongoing":
            _, _, _, Status = self.get()
            self.process_handler.check_status()

        if Status == 'Done':
            print(f'Transmisson Status : {Status}')
            data = {'Sample_Name': Sample_Name, 'Sample_Size': Sample_Size, 'Start': False, 'Status': 'Done'}
            self.set(data)

            tempdata = self.fb.temp_ref.get()
            self.fb.soil_ref.child(Sample_Name).set(tempdata)
            self.fb.temp_ref.delete()



    def NPK_prediction(self,Sample_Name):

        print('predicting.....')

        _, _, _, Status = self.get()

        modelpath = f'{MODEL_PATH}/soil_prediction_model.h5'

        if Status == 'Ongoing':
            print('Please wait, gathering samples')
        else:
            soil_data_ref = self.fb.soil_ref.child(str(Sample_Name))
            data = soil_data_ref.get()

            data = [row for row in data if isinstance(row, list) and len(row) >= 6]
            #print(data)

            if data is None:
                print(f"❌ Sample name '{Sample_Name}' does not exist in {SOIL_DATA_PATH} or No values exist in Sample.")
            else:
                print(f"✅ Sample name '{Sample_Name}' found. Proceeding with data...")
                print(f"Number of samples {len(data)}")

                data_array = np.array(data, dtype=float)
                input = np.mean(data_array, axis=0).reshape(1, -1)

                model = tf.keras.models.load_model(modelpath, custom_objects={'mse': tf.keras.losses.MeanSquaredError()})
                predictions = model.predict(input)
                predictions_list = [round(val, 3) for val in predictions[0].tolist()]


                print("Model Prediction [N P K]:", predictions_list)

                soil_data_ref = self.fb.res_ref.child(str(Sample_Name))
                soil_data_ref.set(predictions_list)

                return predictions_list


    def download_csv(self,Sample_Name):

        soil_data_ref = self.fb.soil_ref.child(str(Sample_Name))
        data = soil_data_ref.get()

        data = [row for row in data if isinstance(row, list) and len(row) >= 6]

        if data is None:
            return 0

        default_filename = f"{Sample_Name}.csv"
        file_path = filedialog.asksaveasfilename(initialfile=default_filename, defaultextension=".csv", filetypes=[["CSV files", "*.csv"]])

        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in data:
                writer.writerow(row)

        return 