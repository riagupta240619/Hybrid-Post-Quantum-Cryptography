import json
import os
from locust import HttpUser, between, task

DEVICE_ID=os.getenv("LOADTEST_DEVICE_ID","loadtest-device")

class PQShieldUser(HttpUser):
    wait_time=between(0.2,1.0)

    def on_start(self):
        self.sequence=0
        self.client.get("/api/v1/health",name="health")

    @task(5)
    def health(self):
        self.client.get("/api/v1/health",name="health")

    @task(3)
    def crypto_info(self):
        self.client.get("/api/v1/crypto/info",name="crypto_info")

    @task(2)
    def publish_telemetry(self):
        self.sequence += 1
        payload={"device_id":DEVICE_ID,"sequence":self.sequence,"telemetry":{"temperature_c":24.0+(self.sequence%10)/10,"humidity_percent":60.0,"battery_percent":90,"sequence":self.sequence}}
        self.client.post("/api/v1/iot/publish",data=json.dumps(payload),headers={"Content-Type":"application/json"},name="iot_publish")
