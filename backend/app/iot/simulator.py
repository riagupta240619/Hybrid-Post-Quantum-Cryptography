from __future__ import annotations
import json, os, time
from urllib.request import Request, urlopen
BACKEND_URL=os.getenv("BACKEND_URL","http://backend:8000").rstrip("/")
DEVICE_ID=os.getenv("DEVICE_ID","temperature-sensor-001")
INTERVAL=float(os.getenv("SIMULATOR_INTERVAL","5"))

def post(path:str,payload:dict|None=None)->tuple[int,dict]:
    data=json.dumps(payload).encode("utf-8") if payload is not None else None
    request=Request(f"{BACKEND_URL}/api/v1{path}",data=data,headers={"Content-Type":"application/json"},method="POST")
    with urlopen(request,timeout=20) as response: return response.status,json.loads(response.read().decode("utf-8"))

def ensure_device()->None:
    try: status,_=post("/devices",{"device_id":DEVICE_ID,"device_type":"temperature-sensor"})
    except Exception as error:
        if "409" not in str(error): raise
    status,_=post(f"/security/devices/{DEVICE_ID}/provision")
    if status not in (200,201): raise RuntimeError(f"Provisioning failed: HTTP {status}")

def publish(sequence:int)->None:
    telemetry={"temperature_c":round(22.0+(sequence%20)*0.17,2),"humidity_percent":round(55+(sequence%15)*0.4,2),"battery_percent":max(20,97-sequence//10),"sequence":sequence}
    status,_=post("/iot/publish",{"device_id":DEVICE_ID,"telemetry":telemetry,"sequence":sequence})
    if status!=202: raise RuntimeError(f"Telemetry publish failed: HTTP {status}")
    print(f"published identity-aware encrypted telemetry for {DEVICE_ID}: {telemetry}",flush=True)

def main()->None:
    ensure_device(); sequence=0
    while True:
        publish(sequence); sequence+=1; time.sleep(INTERVAL)

if __name__=="__main__": main()
