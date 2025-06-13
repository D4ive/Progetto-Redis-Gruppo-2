import subprocess
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    consumer_path = os.path.join(base_dir, "consumer.py")
    producer_path = os.path.join(base_dir, "producer.py")

    # Start consumer.py in a new terminal window
    subprocess.Popen(
        f'start cmd /k python "{consumer_path}"',
        shell=True
    )

    # Start producer.py in a new terminal window
    subprocess.Popen(
        f'start cmd /k python "{producer_path}"',
        shell=True
    )