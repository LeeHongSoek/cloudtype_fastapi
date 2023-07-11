from datetime import datetime
import pytz

timezone = pytz.timezone('Asia/Seoul')

with open('wf_testJob.txt', 'w') as f:
    f.write(f"현재 한국의 작업시간은 : {datetime.now(timezone)} 입니다.")

