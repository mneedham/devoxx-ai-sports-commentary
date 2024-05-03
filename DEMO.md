= Demo Script

Start Redpanda

```bash
docker compose up
```

Go to http://localhost:8080/overview


Create a topic 

```
rpk topic create points -p 5
```

View events

```bash
cat data/1316.json | head -n1 | jq
```

Ingest events

```bash
poetry run python publish_events.py
```

View events

```bash
kcat -C -b localhost:9092 -t points
```