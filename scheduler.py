import schedule
import time
import subprocess

def run_app():
    subprocess.call(["streamlit", "run", "app.py"])

schedule.every().monday.at("18:15").do(run_app)
schedule.every().tuesday.at("18:15").do(run_app)
schedule.every().wednesday.at("18:15").do(run_app)
schedule.every().thursday.at("18:15").do(run_app)
schedule.every().friday.at("18:15").do(run_app)

print("📅 Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(60)