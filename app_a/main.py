from fastapi import FastAPI
import pandas as pd
import requests

app = FastAPI()
CONTAINER_B_URL = "http://container_b:8000/receive-data"
#url = "http://localhost:8001/receive-data"

@app.get("/send-csv")
def send_csv():
    try:
        print("Reading CSV...")
        df = pd.read_csv("data.csv")
        data = df.to_dict(orient="records")
        print("CSV Data:", data)

        print("Sending data to Container B...")
        response = requests.post(CONTAINER_B_URL, json=data)
        print("Response from B:", response.text)

        return {"status": "sent", "container_b_response": response.json()}
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
