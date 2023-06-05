<br/>
<br/>

<p align="center">
<img src="https://files.cloudtype.io/logo/cloudtype-logo-horizontal-black.png" width="50%" alt="Cloudtype"/>
</p>

<br/>
<br/>

# FastAPI

Python으로 구현된 FastAPI 어플리케이션 템플릿입니다.

## 🖇️ 준비 및 확인사항

### 지원 Python 버전

- 3.7, 3.8, 3.9, 3.10, 3.11
- FastAPI는 최소 3.7 버전의 Python를 필요로 합니다.
- ⚠️ 로컬/테스트 환경과 클라우드타입에서 설정한 Python 버전이 상이한 경우 정상적으로 빌드되지 않을 수 있습니다.

### 패키지 명세

- 빌드 시 어플리케이션에 사용된 패키지를 설치하기 위해서는 `requirements.txt` 파일이 반드시 필요합니다.

## ⌨️ 명령어

### Start

```bash
uvicorn main:app --host=0.0.0.0 --port=8000
```

## 🏷️ 환경변수

## 💬 문제해결

- [클라우드타입 Docs](https://docs.cloudtype.io/)
- [클라우드타입 FAQ](https://help.cloudtype.io/guide/faq)
- [Discord](https://discord.gg/U7HX4BA6hu)

## 📄 License

[MIT](https://github.com/tiangolo/fastapi/blob/master/LICENSE)



# websocket([https://fastapi-asyncview.onrender.com](https://fastapi-asyncview.onrender.com/))

이 예제에서는 WebSocket을 사용하여 작업 상태를 클라이언트에 전달합니다.

클라이언트는 WebSocket을 통해 작업의 진행 상황을 주기적으로 수신할 수 있습니다.

long_running_task 함수는 작업의 진행 상태를 지속적으로 업데이트하고,

업데이트된 상태를 클라이언트로 전송합니다.

여기서는 1초마다 업데이트를 수행하도록 하였습니다.

작업이 완료되면 "작업 완료!" 메시지를 클라이언트로 전송합니다.

run_long_task 함수는 WebSocket 연결을 수락하고, 작업 상태 업데이트를 위해

long_running_task를 비동기 작업으로 실행합니다.

작업이 완료될 때까지 대기하고, 클라이언트가 연결을 끊으면 작업을 취소합니다.

클라이언트에서는 WebSocket을 통해 상태 업데이트를 수신하고 처리할 수 있습니다.

이를 통해 작업의 진행 상태를 실시간으로 확인할 수 있습니다.

이 예제는 WebSocket을 사용하여 작업 상태를 업데이트하고 클라이언트에 전달하는 방법을 보여줍니다.

필요에 따라 작업 상태를 데이터베이스에 저장하거나 다른 방법으로 전달할 수도 있습니다.

uvicorn FastApi_asyncView:app --reload --host=0.0.0.0 --port=10000

uvicorn FastApi_Websocket:app --reload  --host=0.0.0.0 --port=10000

taskkill /f /im python.exe         프로세서를 완전히 죽이고 하자.. 씨벌 좃같네

pip install wsproto

pip install fastapi

pip install wsproto

pip install websockets

pip install requests

pip install uvicorn

pip install jinja2

pip install asynci
