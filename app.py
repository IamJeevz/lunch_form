from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime
import pytz

now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
now_ist = now_utc.astimezone(pytz.timezone("Asia/Kolkata"))


app = Flask(__name__)

# Google Form and Webhook URLs
form_url = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdkTf1WS5b8oosWrwAtqkAa_W10blt05LB5cjQqmJZ2W0z4MA/formResponse"
webhook_url = "https://script.google.com/macros/s/AKfycbzfQgeLXCBJtVCXa9AP-ncv_OyySypygv1GW7thsEkgKRIq8ixFBXhtq4CEl6G4XZWZMg/exec"

# Users
user_list = {
    "Jeevan Saju": "PTPL423",
    "Agna TA": "PTPL435",
    "Dibin Thomas": "PTPL431",
    "Sreejith Raghavan": "PTPL394",
    "Gleetas S": "PTPL430",
    "Sanjay Sajeevan": "PTPL453",
    "Bilny Eldho": "PTPL384"
}

@app.route("/")
def index():
    return render_template("index.html", users=user_list.keys())

@app.route("/submit", methods=["POST"])
def submit_lunch():
    data = request.json
    selected_names = data.get("names", [])

    responses = []

    for name in selected_names:
        emp_id = user_list.get(name)
        if not emp_id:
            continue

        form_data = {
            "entry.736127819": name,
            "entry.1569168623": emp_id,
            "entry.700798306": "Yes"
        }

        try:
            form_resp = requests.post(form_url, data=form_data)
            form_status = form_resp.status_code
        except Exception as e:
            form_status = f"Form error: {e}"

        now = datetime.now()
        payload = {
            "date": now_ist.strftime("%Y-%m-%d"),
            "time": now_ist.strftime("%H:%M:%S"),
            "name": name,
            "emp_id": emp_id,
            "lunch": "Yes",
            "status": str(form_status)
        }

        try:
            sheet_resp = requests.post(webhook_url, json=payload)
            sheet_status = sheet_resp.text
        except Exception as e:
            sheet_status = f"Sheet error: {e}"

        responses.append({
            "name": name,
            "form": form_status,
            "sheet": sheet_status
        })

    return jsonify(responses)
    
@app.route("/thanks")
def thanks():
    return render_template("thanks.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

