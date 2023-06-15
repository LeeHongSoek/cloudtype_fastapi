'''
주어진 코드는 Git 저장소의 변경 사항을 주기적으로 확인하고, 
변경된 파일이 있을 경우 자동으로 커밋하고 푸시하는 스크립트입니다.

1. `subprocess` 모듈을 사용하여 외부 프로세스를 실행하기 위해 필요한 함수와 클래스를 제공합니다.
2. `time` 모듈은 시간 관련 기능을 제공하며, `os` 모듈은 운영 체제와 상호 작용하는 기능을 제공합니다.

3. `local_repo` 변수에는 로컬 저장소의 경로를 지정합니다. 이는 Git 저장소가 위치한 디렉토리입니다.
4. `remote_url` 변수에는 원격 저장소의 URL을 지정합니다. 이는 변경 사항을 푸시할 원격 저장소입니다.

5. `os.chdir(local_repo)`를 사용하여 현재 작업 디렉토리를 로컬 저장소의 경로로 변경합니다.
6. `subprocess.call(["git", "remote", "add", "origin", remote_url])`를 사용하여 원격 저장소를 추가합니다. `git remote add` 명령을 실행하여 원격 저장소의 URL과 이름(origin)을 설정합니다.

7. `while True:` 루프는 무한히 반복됩니다. 코드를 중단하려면 종료 조건을 추가해야 합니다.
8. `subprocess.run(["git", "pull", "origin", "main"])`을 사용하여 원격 저장소의 변경 사항을 가져옵니다. `git pull` 명령을 실행하여 원격 저장소의 "main" 브랜치에서 변경 사항을 가져옵니다.
9. `subprocess.run(["git", "status"], capture_output=True, text=True)`을 사용하여 현재 Git 저장소의 상태를 확인합니다. `git status` 명령을 실행하고 출력 결과를 `result` 변수에 저장합니다.
10. `subprocess.run(["git", "add", "."])`를 사용하여 변경된 모든 파일을 스테이징합니다. `git add .` 명령을 실행하여 변경된 모든 파일을 스테이징 영역에 추가합니다.
11. `num_files` 변수에는 변경된 파일의 수를 저장합니다. 이는 `result.stdout`에서 개행 문자를 기준으로 분리한 줄의 개수에서 1을 뺀 값입니다.
12. `num_files > 0` 조건을 사용하여 변경된 파일이 있는 경우에만 아래의 코드를 실행합니다.
13. `subprocess.run(["git", "commit", "-m", "Auto-commit"])`을 사용하여 커밋을 수행합니다. `git commit -m "Auto-commit"` 명령을 실행하여 자동 커밋을 수행합니다.
14. `subprocess.run(["git", "push", "origin", "main"])`을 사용하여 푸시를 수행합니다. `git push origin main` 명령

'''
import subprocess
import time
import os
import datetime
import pytz

# 로컬 저장소의 경로
local_repo = r"C:\MyProject\cloudtype_fastapi"

# 원격 저장소의 URL
remote_url = "https://github.com/LeeHongSoek/cloudtype_fastapi.git"

# 로컬 저장소로 이동합니다.
os.chdir(local_repo)

# 원격 저장소를 추가합니다.
subprocess.call(["git", "remote", "add", "origin", remote_url])

while True:

    # 한국 타임존을 설정합니다.
    # 형식에 맞게 현재 시간을 얻습니다.
    formatted_time = datetime.datetime.now(pytz.timezone("Asia/Seoul")).strftime("%Y / %m / %d  %H : %M")

    # 원격 저장소의 변경 사항을 가져옵니다.
    subprocess.run(["git", "pull", "origin", "main"])

    # git status
    result = subprocess.run(["git", "status"], capture_output=True, text=True)

    # git add --all
    subprocess.run(["git", "add", "."])

    # 변경된 파일의 수
    num_files = len(result.stdout.splitlines()) - 1

    # 변경된 파일이 있는 경우 커밋하고 푸시합니다.
    if num_files > 0:
        subprocess.run(["git", "commit", "-m", f"-- {formatted_time} --"])
        subprocess.run(["git", "push", "origin", "main"])


    # 10 초 동안 대기합니다. 
    #time.sleep(10)
    break
