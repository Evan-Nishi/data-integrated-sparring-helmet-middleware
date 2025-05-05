import requests
import json
from dotenv import load_dotenv
import os
from impact import impact
from tensorflow.keras.models import load_model
import numpy as np

load_dotenv()

class dbSession:
    def __init__(self, helmet_id=None, predict=True):
        load_dotenv()
        if (helmet_id is None):
            self.helmet_id = int(os.getenv("HELMET_ID"))
        else:
            self.helmet_id = helmet_id

        if (predict):
            with open('label_map.json', 'r') as f:
                self.label_map = json.load(f)
            self.hit_model = load_model('hit_classifier_model.keras')
        
        self.uri = os.getenv("BASE_URI")
        
        self.session_active = False
        self.defaultHeaders = {'Content-Type': 'application/json'}

    
    def start_session(self, headers = None,):
        if headers is None: 
            headers = self.defaultHeaders

        #TODO: add auth token
        #'authToken': authToken
        payload = {'data': { 'helmetNum':self.helmet_id}}

        res = requests.post(f'{self.uri}/beginSession', headers=headers, data=json.dumps(payload))
        print(f'{self.uri}/beginSession')
        
        if res.status_code == 200:
            print("session started")

            self.session_active = True
            #session_data = res.json()
            #self.session_id = session_data['sessionid']
            return True
        else:
            print("session failed to start")
            return False
    
    #TODO: have content built from params, not passed in whole
    def add_impact_data(self, impact: impact, headers = None):
        if headers is None: 
            headers = self.defaultHeaders

        input_data = np.array([[impact.x, impact.y, impact.z, impact.gx, impact.gy, impact.gz]])
        input_data = input_data.astype('float32')

        prediction = self.hit_model.predict(input_data)
        predicted_class = np.argmax(prediction, axis=1)

        if self.session_active == True:
            payload = {
                'data':{
                    'helmetNum': self.helmet_id,
                    'content': (impact.payload_obj()),
                    'type': self.label_map[str(predicted_class[0])]
                }
            }
            print("predicted:",self.label_map[str(predicted_class[0])])

            res = requests.post(f'{self.uri}/hitReg', headers=headers, data=json.dumps(payload))

            if res.status_code == 200:
                return True
            else:
                print('data failed to post')
                print(res.content)
                return False
        else:
            print('session not active yet')
            return False
        
    def end_session(self, headers = None):
        if headers is None: 
            headers = self.defaultHeaders

        if self.session_active:
            payload = {
                'data': {
                    'helmetNum': self.helmet_id
                    #sessionID: self.sessionID,
                    #authToken: self.authToken
                }
            }

            res = requests.post(f'{self.uri}/endSession', headers=headers, data=json.dumps(payload))
            if res.status_code == 200:
                self.session_active = False
                return True
            else:
                print('session failed to end')
        else:
            print('no active session to terminate')
        