from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime
import pytz
import os

app = Flask(__name__)

# Google Form and Webhook URLs
form_url = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdzpcp9FuxahnbdyBJMEZY6VNkieVAJoSJi_W8F5QDA2WWV2A/formResponse"
webhook_url = "https://script.google.com/macros/s/AKfycbzkGyMtCEuJTDclad333-_mpbDkxORXsFcyVHcdJevikCplO6UtN7kGXvyViMdGnS_j/exec"

# Users
user_list = {
    "Jeevan Saju": "PTPL423",
    "Agna TA": "PTPL435",
    "Dibin Thomas": "PTPL431",
    "Sreejith Raghavan": "PTPL394",
    "Gleetas S": "PTPL430",
    "Sanjay Sajeevan": "PTPL453",
    "Bilny Eldho": "PTPL384",
	"Shahazin PS" : "NIL",
	"Augnase George" : "NIL"
}

@app.route("/")
def index():
    return render_template("index.html", users=user_list.keys())

@app.route("/submit", methods=["POST"])
def submit_lunch():
    # Handle both JSON and Form submissions
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict(flat=False)

    selected_names = data.get("names", [])

    # If names is string (from form), convert to list
    if isinstance(selected_names, str):
        selected_names = [selected_names]

    responses = []

    for name in selected_names:
        emp_id = user_list.get(name)
        if not emp_id:
            continue

        # Data for Google Form
        form_data = {
            "entry.624210802": name,
            "entry.1158356341": emp_id,
            "entry.769903343": "Yes",
            "pageHistory": "0,1" 
        }

        try:
            form_resp = requests.post(form_url, data=form_data)
            form_status = form_resp.status_code
        except Exception as e:
            form_status = f"Form error: {e}"

        # Get IST time
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        now_ist = now_utc.astimezone(pytz.timezone("Asia/Kolkata"))

        # Payload for Google Sheet webhook
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

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    return response

if __name__ == "__main__":
     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)      
