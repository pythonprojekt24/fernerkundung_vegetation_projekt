# download von datein aus Google Drive
# das skript funktioniert
# dafür habe ich auf meiner google cloud ein dienstkonto gmacht damit ich nicht komploziert mit anwender konfuguration authethfizierung brauche
# ich habe bei google drive außerdem sicher gestellt, dass mein dienstkonto zugriff auf die datein im ordner EarthEngineImage hat
# wichtig ist auch noch vom dienstkonto eine schlüssel .json file mit den zugriff informationen herunterzuladen
# die file_id von der Datei kann man nachschauen auf google drive (der link den die datei hat)

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os

# Pfad zur JSON-Schlüssel-Datei Ihres Servicekontos
service_account_file = r"C:\Users\jomas\YourUsername\ee_mascherjo_driveschluessel.json"

# ID der Datei auf Google Drive, die heruntergeladen werden soll
file_id = '17yagjyvC05ViLuwWjjCPU5plhnYRM91J' 

# Zielordner und Dateiname für den Download
download_directory = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM"
file_name = 'middle_europe.tif'

# Erstellen Sie eine Authentifizierungsinstanz für das Servicekonto
credentials = service_account.Credentials.from_service_account_file(
    service_account_file,
    scopes=['https://www.googleapis.com/auth/drive']  # Hier wird 'drive' verwendet, nicht 'drive.readonly'
)

# Erstellen Sie eine Drive-API-Instanz
drive_service = build('drive', 'v3', credentials=credentials)

# Herunterladen der Datei von Google Drive
request = drive_service.files().get_media(fileId=file_id)
fh = io.FileIO(os.path.join(download_directory, file_name), mode='wb')
downloader = MediaIoBaseDownload(fh, request)

# Führen Sie den Download durch und speichern Sie die Datei lokal
done = False
while not done:
    status, done = downloader.next_chunk()
    print(f"Download {int(status.progress() * 100)}%.")

# print(f"Download abgeschlossen. Die Datei wurde unter {download_directory + '\\' + file_name} gespeichert.")

download_path = os.path.join(download_directory, file_name)
print(f"Download abgeschlossen. Die Datei wurde unter {download_path} gespeichert.")
