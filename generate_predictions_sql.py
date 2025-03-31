import json

with open("predictions.json") as f:
    predictions = json.load(f)

with open("predictions.sql", "w") as f:
    for entry in predictions:
        db_id = entry["db_id"]
        sql = entry["sql"].strip().replace("\n", " ")
        f.write(f"{db_id}\t{sql}\n")

print("✅ Saved predictions.sql")