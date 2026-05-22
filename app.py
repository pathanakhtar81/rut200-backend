from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

latest_data = {
    "status": "OFFLINE",
    "last_update": "--:--:--",
    "Average_VN": 0,
    "R_N": 0,
    "Y_N": 0,
    "B_N": 0,
    "Average_Amp": 0
}

excel_file = "historical_data.xlsx"
last_excel_save = 0


@app.route('/api/rutdata', methods=['POST'])
def receive_data():

    global latest_data, last_excel_save

    data = request.get_json(force=True)

    try:
        values = data["Modbus_data"]["data"].split(',')

        if len(values) < 5:
            return jsonify({"status": "invalid data"})

        avg_vn = float(values[0])
        r_n = float(values[1])
        y_n = float(values[2])
        b_n = float(values[3])
        avg_amp = float(values[4])

    except:
        return jsonify({"status": "parse error"})

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    latest_data = {
        "status": "ONLINE",
        "last_update": current_time,
        "Average_VN": avg_vn,
        "R_N": r_n,
        "Y_N": y_n,
        "B_N": b_n,
        "Average_Amp": avg_amp
    }

    now = time.time()

    if now - last_excel_save >= 60:

        row = {
            "Time": current_time,
            "Average_VN": avg_vn,
            "R_N": r_n,
            "Y_N": y_n,
            "B_N": b_n,
            "Average_Amp": avg_amp
        }

        df = pd.DataFrame([row])

        if os.path.exists(excel_file):
            old = pd.read_excel(excel_file)
            df = pd.concat([old, df], ignore_index=True)

        df.to_excel(excel_file, index=False)

        last_excel_save = now
        print("Excel Saved")

    return jsonify({"status": "success"})


@app.route('/api/live', methods=['GET'])
def live():
    return jsonify(latest_data)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
