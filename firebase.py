import firebase_admin
from firebase_admin import credentials, db
from parameters import *

class FirebaseConnect:
    def __init__(self):
        self.cred_path = CRED_PATH
        self.db_url = URL
        self.initialize()

    def initialize(self):
        try:
            cred = credentials.Certificate(self.cred_path)
            firebase_admin.initialize_app(cred, {'databaseURL': self.db_url})
            print("✅ Successfully connected to Firebase Realtime Database")
            self.user_ref = db.reference("Initialization")
            self.soil_ref = db.reference("Soil_Data")
            self.res_ref = db.reference("results")
            self.temp_ref = db.reference("tempData")
        except Exception as e:
            print("❌ Failed to initialize Firebase connection.")
            print(f"Error: {e}")



firebase_instance = FirebaseConnect()
