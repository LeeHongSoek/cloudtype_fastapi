'''
이 예제에서는 WebSocket을 사용하여 작업 상태를 클라이언트에 전달합니다. 
클라이언트는 WebSocket을 통해 작업의 진행 상황을 주기적으로 수신할 수 있습니다.

long_running_task 함수는 작업의 진행 상태를 지속적으로 업데이트하고, 
업데이트된 상태를 클라이언트로 전송합니다. 
여기서는 1초마다 업데이트를 수행하도록 하였습니다. 
작업이 완료되면 "작업 완료!" 메시지를 클라이언트로 전송합니다.

run_long_running_task 함수는 WebSocket 연결을 수락하고, 작업 상태 업데이트를 위해 
long_running_task를 비동기 작업으로 실행합니다. 
작업이 완료될 때까지 대기하고, 클라이언트가 연결을 끊으면 작업을 취소합니다.

클라이언트에서는 WebSocket을 통해 상태 업데이트를 수신하고 처리할 수 있습니다. 
이를 통해 작업의 진행 상태를 실시간으로 확인할 수 있습니다.

이 예제는 WebSocket을 사용하여 작업 상태를 업데이트하고 클라이언트에 전달하는 방법을 보여줍니다. 
필요에 따라 작업 상태를 데이터베이스에 저장하거나 다른 방법으로 전달할 수도 있습니다.

uvicorn main_asyncView:app --reload  --host=0.0.0.0 --port=10000
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
from starlette.websockets import WebSocket, WebSocketDisconnect
import asyncio
import random
import os


app = FastAPI()

# Register 'static' folder to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# /docs 로 리디렉션 ------------------------------
@app.get("/")
async def root():
    #return {"result": "root"}
    return RedirectResponse(url="/docs")
    # return RedirectResponse(url="/redoc")


# html 화면 호출 ------------------------------
@app.get("/asyncView")
def home_asyncView(request: Request):
    return templates.TemplateResponse("asyncView.html", {"request": request})


# WebSocket 예제.. ---------------------------
@app.websocket("/long_running_task")
async def run_long_running_task(websocket: WebSocket):
    await websocket.accept()

    # 작업 상태 업데이트를 위한 비동기 작업 시작
    task = asyncio.create_task(long_running_task(websocket))

    try:
        # 작업 완료까지 대기
        await task
        await websocket.send_text("작업 완료!")  # Move this line here
    except asyncio.CancelledError:
        # 클라이언트가 연결을 끊을 경우 작업 취소
        task.cancel()
        await task
        

async def long_running_task(websocket: WebSocket):
    stop_requested = asyncio.Event()  # 중지 요청을 나타내는 이벤트 객체

    async def receive_stop_signal():
        while not stop_requested.is_set():
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=0.5)
                if message == "stop":
                    stop_requested.set()  # 중지 요청 설정
                    break
            except asyncio.TimeoutError:
                continue
            except WebSocketDisconnect:
                stop_requested.set()
                break

    # 중지 요청을 받을 수 있는 별도의 태스크 실행
    receive_task = asyncio.create_task(receive_stop_signal())

    max_sec = 5
    # 작업 상태를 지속적으로 업데이트하고 클라이언트에 전달
    for i in range(1, max_sec+1):

        for j in range(1, random.randint(5, 10)):
            print(f" {j}번 수행")
            await websocket.send_text(f"{j}번 수행")

        # 중지 요청이 있을 경우 작업 중지
        if stop_requested.is_set():
            break

        await websocket.send_text(f"작업 진행 중: {max_sec-i}초 남음")
        await asyncio.sleep(1)
