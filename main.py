#!/usr/bin/env python3

import requests
import json
from cryptography.fernet import Fernet
import time
import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog
import shutil

bot_token = "REDACTED"
discord_url = "https://discord.com/api/v10/channels/REDACTED/messages"
key = b'REDACTED'
cipher_suite = Fernet(key)

discord_url_headers = {

    'Authorization':"Bot "+bot_token

}

def process_chunk(chunk,file_path):
    
    time.sleep(1.2)
    encrypted_chunk = cipher_suite.encrypt(chunk)

    data = {'file':("data.bin",encrypted_chunk,'application/octet-stream')}

    response = requests.post(headers=discord_url_headers,files=data,url=discord_url)

    if response.status_code == 200:
        print("Chunk uploaded successfully")
        response_json = response.json()
        message_id = response_json.get('id')
        if message_id:
            originalfilename = os.path.basename(file_path)
            newfilename = f"{originalfilename}.txt"
            file_path = "/Users/Thomas/Documents/Projects/Cloud-storage/storage/"+newfilename
            with open(file_path,'a') as newfile:
                newfile.write(message_id+'\n')
    else:
        print(f"There was an error uploading your file. Error code {response.status_code}. The response from discord API is send below.")
        print(response.text)
        


def upload_file(file_path):
    print("file upload started")
    if file_path:
        print(file_path)
        with open(file_path,'rb') as file:
            while True:
                chunk = file.read(7*1024*1024)
                if not chunk:
                    print("Upload finished.")
                    break
                message_id = process_chunk(chunk,file_path)
    else:
        print("There was an issue with the upload")


def download_file(self,file_name):
    with open("/Users/Thomas/Documents/Projects/Cloud-storage/storage/" + file_name + ".txt", 'r') as file:
        for line in file:
            time.sleep(1.2)
            response = requests.get(url="https://discord.com/api/v10/channels/1337453428993163264/messages/" + line.strip(), headers=discord_url_headers)
            if response.status_code == 200:
                print("Chunk downloaded sucessfully")
                response_json = response.json()
                attachments = response_json.get('attachments',[])

                for attachment in attachments:
                    file_response = requests.get(attachment['url'])

                    if file_response.status_code == 200:
                        with open('temp_file.bin','wb') as f:
                            file_contents = file_response.content
                            f.write(file_contents)
                            message_content_pure = cipher_suite.decrypt(file_contents)
                            with open("/Users/Thomas/Documents/Projects/Cloud-storage/storage/"+file_name,'ab') as file2:
                                file2.write(message_content_pure)

            else:
                print("There was an issue with the retrieval " + str(response.status_code))

    print("Download finished.")
    self.prompt_for_location_and_copy(file_name)


class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("List of available files")
        self.setGeometry(100, 100, 200, 100)
        layout = QVBoxLayout()
        label = QLabel("List of available files \n")
        label.setStyleSheet('font-weight: bold;')
        layout.addWidget(label)
        self.setLayout(layout)
        self.onOpen()

    
    def onOpen(self):

        file_names = []
        for file in os.listdir('/Users/Thomas/Documents/Projects/Cloud-storage/storage/'):
            if file.endswith(".txt"):
                raw_file_name = os.path.splitext(file)[0]
                print(raw_file_name)
                file_names.append(raw_file_name)
        for name in file_names:
            file_label = QLabel(name)
            self.layout().addWidget(file_label)



class CombinedApp(QWidget):
    def __init__(self):
        super().__init__()
        self.second_window = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Discord based cloud storage')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Text input section
        self.label = QLabel('Enter the file name:', self)
        layout.addWidget(self.label)

        self.textBox = QLineEdit(self)
        layout.addWidget(self.textBox)

        self.submitButton = QPushButton('Download file', self)
        self.submitButton.clicked.connect(self.onSubmit)
        layout.addWidget(self.submitButton)

        self.listfiles = QPushButton('List avaliable files', self)
        self.listfiles.clicked.connect(self.listFiles)
        layout.addWidget(self.listfiles)

        self.resultLabel = QLabel('', self)
        layout.addWidget(self.resultLabel)

        # File uploader section
        self.uploadButton = QPushButton('Upload File', self)
        self.uploadButton.clicked.connect(self.showFileDialog)
        layout.addWidget(self.uploadButton)

        self.fileLabel = QLabel('No file selected', self)
        layout.addWidget(self.fileLabel)

        self.setLayout(layout)

    def onSubmit(self):
        input_text = self.textBox.text()
        self.resultLabel.setText(f'You entered: {input_text}')
        print(f'Entered Text: {input_text}')  # Print the entered text to the console
        input_name = input_text
        download_file(self,file_name=input_name)

    def listFiles(self):
        print("Second window opened.")      
        if self.second_window is None:
            self.second_window = SecondWindow()
        self.second_window.show()

    def showFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.fileLabel.setText(f'Selected File: {fileName}')
            print(f'Selected File Path: {fileName}')  # Print the file path to the console
            file_path = fileName
            upload_file(file_path=fileName)
    def prompt_for_location_and_copy(self, file_name):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        download_location = QFileDialog.getSaveFileName(self, "Save here",file_name, options=options)
        if download_location:
            source_file = "/Users/Thomas/Documents/Projects/Cloud-storage/storage/" + file_name
            # shutil.copy(source_file, download_location)
            print(download_location)

            shutil.move(source_file,download_location[0])
            print(f"File copied to {download_location}")
        else:
            print("No folder selected")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CombinedApp()
    ex.show()
    sys.exit(app.exec_())

window = QWidget()
window.setWindowTitle('Discord based cloud storage')
window.setGeometry(100, 100, 300, 200)


# Show the window
window.show()

# Run the application's event loop
sys.exit(app.exec_())
