import schedule, os, time

def job():
    os.system('python src/parse_logs.py')
    os.system('python src/detect_isoforest.py')
    os.system('python src/generate_report.py')
    print("Cycle completed ✅")

schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
