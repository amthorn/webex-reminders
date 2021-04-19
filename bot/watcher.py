import datetime
import json
import time

from controller import Controller

controller = Controller()


def main() -> None:
    # Relax
    keys = controller.db.keys()  # Atomic to avoid multithreading issues since we don't use a lock
    now = datetime.datetime.utcnow().timestamp()
    for key in keys:
        timestamp = float(key.decode())
        if now >= timestamp:
            print(f"Delivering reminder {timestamp}")
            # Trigger reminder
            controller.api.messages.create(**json.loads(controller.db.get(key).decode()))

            # atomic db pop
            controller.db.delete(key)
    time.sleep(1)


if __name__ == "__main__":
    print("Relaxing...")
    while True:
        try:
            main()
        except Exception as e:
            print(e)
