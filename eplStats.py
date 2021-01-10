
import speech_recognition as sr
import re
import threading
import time

import requests
import json
import pyttsx3

API_KEY="tJX123RE0dAt"
PROJECT_TOKEN="tODKhwTx-jAT"
RUN_TOKEN="ts5EnyUrCpw-"

class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
        data = json.loads(response.text)
        return data

    def get_club_info(self, epl):
        data=self.data["epl"]
        for content in data:
            if content['club'].lower() == epl.lower():
                return content
        return "0"

    def get_list_of_clubs(self):
        clubs = []
        for club in self.data['epl']:
            clubs.append(club['club'].lower())

        return clubs



def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))


    return said.lower()

def main():
    print("Program has started")
    data = Data(API_KEY, PROJECT_TOKEN)
    END_PHRASE = "stop"
    club_list = data.get_list_of_clubs()

    UPDATE_COMMAND = "update"
    
    CLUB_PATTERNS = {
                    re.compile("[\w\s]+ wins [\w\s]+"): lambda epl: data.get_club_info(epl)['wins'],
                    re.compile("[\w\s]+ loses [\w\s]+"): lambda epl: data.get_club_info(epl)['loses'],
                    re.compile("[\w\s]+ points [\w\s]+"): lambda epl: data.get_club_info(epl)['points'],
                    re.compile("[\w\s]+ position [\w\s]+"): lambda epl: data.get_club_info(epl)['position'],
                    }

    

    while True:
        print("Listening...")
        text = get_audio()
        print(text)
        result = None

        for pattern, func in CLUB_PATTERNS.items():
            if pattern.match(text):

                words = set(text.split(" "))
                for club in club_list:
                    if club in words:
                        result = func(club)
                        break

        if text == UPDATE_COMMAND:
            result = "Data is being updated"
            data.update_data()

        if result:
            speak(result)

        if text.find(END_PHRASE) != -1:
            print("Exit")
            break


main()
    
