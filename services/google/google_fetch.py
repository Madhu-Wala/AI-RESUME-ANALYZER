import gspread
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import io
import os


# 🔹 Extract sheet ID from URL
def get_sheet_id(sheet_url):
    return sheet_url.split("/d/")[1].split("/")[0]


# 🔹 Extract file ID from Drive link
def get_file_id(link):
    if "id=" in link:
        return link.split("id=")[1]
    elif "/d/" in link:
        return link.split("/d/")[1].split("/")[0]
    else:
        raise ValueError("Invalid Google Drive link format")


# 🔹 Create Google clients using OAuth credentials
def get_clients(session_creds):
    creds = Credentials(**session_creds)

    gspread_client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)

    return gspread_client, drive_service


# 🔹 Fetch sheet data
def fetch_sheet_data(sheet_url, session_creds):
    client, _ = get_clients(session_creds)

    sheet_id = get_sheet_id(sheet_url)
    sheet = client.open_by_key(sheet_id).sheet1

    rows = sheet.get_all_records()
    return rows


# 🔹 Download file from Drive
def download_file(service, file_id, filename):
    request = service.files().get_media(fileId=file_id)

    fh = io.FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()


# 🔥 MAIN FUNCTION: Fetch + Download resumes
def fetch_resumes(sheet_url, session_creds):
    rows = fetch_sheet_data(sheet_url, session_creds)
    _, drive_service = get_clients(session_creds)

    os.makedirs("resumes", exist_ok=True)

    for i, row in enumerate(rows):
        try:
            name = row.get("Name", f"candidate_{i}")
            link = row.get("Submit your resume")

            if not link:
                continue

            file_id = get_file_id(link)
            filename = f"resumes/{name}_{i}.pdf"

            # Avoid re-downloading
            if os.path.exists(filename):
                continue

            download_file(drive_service, file_id, filename)
            print(f"Downloaded: {filename}")

        except Exception as e:
            print(f"Error processing row {i}: {e}")
    return rows