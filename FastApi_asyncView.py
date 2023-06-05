'''
이 예제에서는 WebSocket을 사용하여 작업 상태를 클라이언트에 전달합니다. 
클라이언트는 WebSocket을 통해 작업의 진행 상황을 주기적으로 수신할 수 있습니다.

long_running_task 함수는 작업의 진행 상태를 지속적으로 업데이트하고, 
업데이트된 상태를 클라이언트로 전송합니다. 
여기서는 1초마다 업데이트를 수행하도록 하였습니다. 
작업이 완료되면 "작업 완료!" 메시지를 클라이언트로 전송합니다.

run_websocket 함수는 WebSocket 연결을 수락하고, 작업 상태 업데이트를 위해 
long_running_task를 비동기 작업으로 실행합니다. 
작업이 완료될 때까지 대기하고, 클라이언트가 연결을 끊으면 작업을 취소합니다.

클라이언트에서는 WebSocket을 통해 상태 업데이트를 수신하고 처리할 수 있습니다. 
이를 통해 작업의 진행 상태를 실시간으로 확인할 수 있습니다.

이 예제는 WebSocket을 사용하여 작업 상태를 업데이트하고 클라이언트에 전달하는 방법을 보여줍니다. 
필요에 따라 작업 상태를 데이터베이스에 저장하거나 다른 방법으로 전달할 수도 있습니다.

uvicorn FastApi_asyncView:app --reload  --host=0.0.0.0 --port=10000
taskkill /f /im python.exe         프로세서를 완전히 죽이고 하자.. 씨벌 좃같네

pip install fastapi
pip install wsproto
pip install websockets
pip install --upgrade requests

'''
from fastapi import FastAPI, Request
from fastapi import WebSocket
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os


app = FastAPI()

# Register 'static' folder to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    #return {"result": "root"}
    return RedirectResponse(url="/docs")
    # return RedirectResponse(url="/redoc")


@app.get("/asyncView")
def home_asyncView(request: Request):
    return templates.TemplateResponse("asyncView.html", {"request": request})

