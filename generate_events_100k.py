import csv
import uuid
import random
import datetime
import json
import os

os.makedirs("data", exist_ok=True)
output_path = "data/events_test.csv"

now = datetime.datetime.now()
event_types = ["view_item", "login", "app_open", "logout", "add_to_cart"]
countries = ["PL", "SE", "NL", "RO", "KZ"]
os_list = ["iOS", "Android", "Windows", "macOS"]
app_versions = ["1.8.6", "1.8.9", "1.9.6", "2.0.1"]

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["event_id", "occurred_at", "user_id", "event_type", "properties_json"])
    writer.writeheader()
    for i in range(100_000):
        user_id = random.randint(1, 5000)
        event_type = random.choice(event_types)
        props = {
            "country": random.choice(countries),
            "session_id": str(uuid.uuid4())
        }
        # Добавляем дополнительные поля в зависимости от event_type
        if event_type == "view_item" or event_type == "add_to_cart":
            props.update({
                "item_id": f"SKU{random.randint(100, 999)}",
                "qty": random.randint(1, 5),
                "price": round(random.uniform(10, 500), 2),
                "currency": "USD"
            })
        elif event_type == "login" or event_type == "logout":
            props.update({
                "method": random.choice(["apple", "google", "password"])
            })
        elif event_type == "app_open":
            props.update({
                "os": random.choice(os_list),
                "app_version": random.choice(app_versions)
            })

        writer.writerow({
            "event_id": str(uuid.uuid4()),
            "occurred_at": (now - datetime.timedelta(minutes=i % 1000)).isoformat(),
            "user_id": user_id,
            "event_type": event_type,
            "properties_json": json.dumps(props, ensure_ascii=False)
        })

print(f"✅ Сгенерировано 100,000 событий в {output_path}")
