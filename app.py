from flask import Flask, request, jsonify, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# Google Sheets config
SERVICE_ACCOUNT_FILE = "auth.json"  # path to your service account file
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("sheets", "v4", credentials=creds)

# Your sheet
SHEET_ID = "10GYUWOq36W3XS3ySW1PcPwuvI6t-j47bu9jW7eJ8isQ"
RANGE = "Sheet1!A:B"   # update if your tab is named differently


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/exercises", methods=["GET"])
def get_exercises():
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=RANGE
    ).execute()
    values = result.get("values", [])

    exercises = []
    # Skip header row, start indexing from row 2
    for i, row in enumerate(values[1:], start=2):
        exercise = row[0] if len(row) > 0 else ""
        count = row[1] if len(row) > 1 else "0"
        exercises.append({"row": i, "exercise": exercise, "count": count})

    return jsonify(exercises)


@app.route("/api/add/<int:row>", methods=["POST"])
def add_to_exercise(row):
    """Add count to the existing exercise in a specific row"""
    data = request.json
    add_count = int(data.get("count", 0))

    # Get current row values
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=f"Sheet1!A{row}:B{row}"
    ).execute()
    values = result.get("values", [["", "0"]])

    exercise = values[0][0] if values[0] else ""
    old_count = int(values[0][1]) if len(values[0]) > 1 else 0
    new_count = old_count + add_count

    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"Sheet1!A{row}:B{row}",
        valueInputOption="USER_ENTERED",
        body={"values": [[exercise, new_count]]},
    ).execute()

    return jsonify({"status": "updated", "exercise": exercise, "new_count": new_count})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
