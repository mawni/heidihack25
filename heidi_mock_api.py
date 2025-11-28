from flask import Flask, jsonify
import threading

app = Flask(__name__)

patients = [
    {
        "id": 1,
        "name": "John Doe",
        "dob": "1980-05-15",
        "prescription": "Atorvastatin 10mg",
        "symptoms": ["headache", "fatigue"],
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "dob": "1975-09-30",
        "prescription": "Metformin 500mg",
        "symptoms": ["thirst", "blurred vision"],
    },
    {
        "id": 3,
        "name": "Alice Brown",
        "dob": "1992-12-10",
        "prescription": "Lisinopril 20mg",
        "symptoms": ["cough", "dizziness"],
    },
]


@app.route("/patients", methods=["GET"])
def get_patients():
    return jsonify({"patients": patients})


def run_api():
    app.run(port=5000, debug=False)


if __name__ == "__main__":
    thread = threading.Thread(target=run_api, daemon=True)
    thread.start()
    print("API running in background on http://127.0.0.1:5000/patients")
    input("Press Enter to exit...\n")
