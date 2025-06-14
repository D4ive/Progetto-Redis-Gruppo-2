import subprocess
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    consumer_path = os.path.join(base_dir, "consumer.py")
    producer_path = os.path.join(base_dir, "producer.py")

    print("Benvenuto nel Sistema di Notifiche Redis!")
    inp = input("Digita: \n1. se sei un consumatore di notifiche, \n2. se sei un produttore di notifiche.\n")

    while (inp.strip() not in ["1", "2"]):
        inp = input("Scelta non valida. Digita 1 o 2: ").strip()
    if inp == "1":
        subprocess.Popen(
            f'start cmd /k python "{consumer_path}"',
            shell=True
        )
    else:
        subprocess.Popen(
            f'start cmd /k python "{producer_path}"',
            shell=True
        )