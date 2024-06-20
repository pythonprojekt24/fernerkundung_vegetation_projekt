from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

# Authenticate and create the PyDrive client.
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # This will open a web browser for authentication.
drive = GoogleDrive(gauth)

# Replace with the folder ID or name in your Google Drive
folder_name = 'EarthEngineImages'
file_name = 'elevation_europe.tif'  # Change to the name of your exported file

# Search for the file in the specified folder
file_list = drive.ListFile({'q': f"title contains '{file_name}' and '{folder_name}' in parents"}).GetList()

if file_list:
    file = file_list[0]
    print(f"Downloading {file['title']} from Google Drive...")
    file.GetContentFile(file['title'])
    print(f"Downloaded {file['title']} to {os.path.abspath(file['title'])}")
else:
    print(f"No file named {file_name} found in folder {folder_name}")
