import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

class dbSession:
    def __init__(self, helmet_id=None):
        load_dotenv()
        if (helmet_id is None):
            self.helmet_id = int(os.getenv("HELMET_ID"))
        else:
            self.helmet_id = helmet_id

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
    def add_impact_data(self, content, headers = None):
        if headers is None: 
            headers = self.defaultHeaders

        if self.session_active == True:


            payload = {
                'data':{
                    'helmetNum': self.helmet_id,
                    'content': content 
                    #'sessionID': self.sessionID
                }
            }
            res = requests.post(f'{self.uri}/hitReg', headers=headers, data=json.dumps(payload))

            if res.status_code == 200:
                return True
            else:
                print('data failed to post')
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
        