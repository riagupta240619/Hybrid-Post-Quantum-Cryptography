from __future__ import annotations
import os,time
import requests
BACKEND_URL=os.getenv("BACKEND_URL","http://backend:8000").rstrip("/")
DEVICE_ID=os.getenv("DEVICE_ID","temperature-sensor-001")
INTERVAL=float(os.getenv("SIMULATOR_INTERVAL","5"))

def ensure_device()->None:
    base=f"{BACKEND_URL}/api/v1"
    response=requests.post(f"{base}/devices",json={"device_id":DEVICE_ID,"device_type":"temperature-sensor"},timeout=10)
    if response.status_code not in (201,409): response.raise_for_status()
    provision=requests.post(f"{base}/security/devices/{DEVICE_ID}/provision",timeout=20)
    if provision.status_code not in (201,200): provision.raise_for_status()

def publish(sequence:int)->None:
    telemetry={"temperature_c":round(22.0+(sequence%20)*0.17,2),"humidity_percent":round(55+(sequence%15)*0.4,2),"battery_percent":max(20,97-sequence//10),"sequence":sequence}
    response=requests.post(f"{BACKEND_URL}/api/v1/iot/publish",json={"device_id":DEVICE_ID,"telemetry":telemetry,"sequence":sequence},timeout=20)
    response.raise_for_status()
    print(f"published identity-aware encrypted telemetry for {DEVICE_ID}: {telemetry}",flush=True)

def main()->None:
    ensure_device(); sequence=0
    while True:
        publish(sequence); sequence+=1; time.sleep(INTERVAL)

if __name__=="__main__": main()
