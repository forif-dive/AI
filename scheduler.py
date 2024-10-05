import schedule
import time
import subprocess


def job():
    subprocess.run(["python", "main.py"])


# 매일 자정에 실행
schedule.every().day.at("00:00").do(job)


while True:
    schedule.run_pending()
    time.sleep(1)
