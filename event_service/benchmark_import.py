import time
import os
from event_service.import_events import import_events

if __name__ == "__main__":
    # os.environ["TEST_MODE"] = "1"

    # CSV для бенчмарка
    csv_file = "data/events_100k.csv"
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV файл не найден: {csv_file}")

    start = time.time()
    import_events(csv_file, batch_size=1000)
    elapsed = time.time() - start
    print(f"⏱ Импорт {csv_file} занял: {elapsed:.2f} сек")
