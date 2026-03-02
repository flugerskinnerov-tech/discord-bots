import subprocess
import threading
import sys

def run_bot(name, script):
    print(f"Запуск {name}...")
    subprocess.run([sys.executable, script])

threads = []
threads.append(threading.Thread(target=run_bot, args=("Clans", "clans.py")))
threads.append(threading.Thread(target=run_bot, args=("Logs", "logs.py")))
threads.append(threading.Thread(target=run_bot, args=("Private", "privat.py")))

for t in threads:
    t.start()

for t in threads:
    t.join()