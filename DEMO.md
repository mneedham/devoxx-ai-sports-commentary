= Demo Script

== Redpanda

```bash
docker compose up
```

Create a topic 

```
rpk topic create points -p 5
```

Go to http://localhost:8080/overview

View events

```bash
cat data/1316.json | head -n1 | jq
```

Ingest events

```bash
poetry run python publish_events.py --file data/1316.json
```

View events

```bash
kcat -C -b localhost:9092 -t points
```

<!-- <Back to slides> -->

== ClickHouse

```bash
mkdir clickhouse-server && cd clickhouse-server
./clickhouse server
```

Connect to ClickHouse

```bash
./clickhouse client -mn
```


```sql
CREATE TABLE pointsQueue(
    match_id String,
    id String,
    time String,
    player1 String,
    player2 String,
    previous_sets Array(String),
    server String,
    set String,
    game String,
    set_score String,
    point_score String,
    description String,
    game_winner String,
    publish_time String,
    event_type String,
    event_round String
)
ENGINE = Kafka(
  'localhost:9092', 
  'points', 
  'points-consumer-group', 
  'JSONEachRow'
)
SETTINGS kafka_flush_interval_ms=500;

CREATE TABLE points (
    match_id String,
    id String,
    time String,
    player1 String,
    player2 String,
    previous_sets Array(String),
    server String,
    set String,
    game String,
    set_score String,
    point_score String,
    description String,
    game_winner String,
    publish_time DateTime32,
    event_type String,
    event_round String,
) 
ENGINE = MergeTree 
ORDER BY match_id;

CREATE MATERIALIZED VIEW points_mv TO points AS 
SELECT * REPLACE(
    parseDateTime32BestEffort(publish_time) AS publish_time
)
FROM pointsQueue;
```

> Query the points table

```
cp ../data/matches.csv user_files
```

```sql
CREATE TABLE matches
ORDER BY match_id AS
SELECT * REPLACE(
    toString(match_id) AS match_id
)
FROM file('matches.csv') 
SETTINGS schema_inference_make_columns_nullable=0;
```

## Apps

Commentator Admin 

```bash
cd ..
source .env
poetry run streamlit run apps/commentator.py --server.headless True
```

Live Feed Server

```bash
poetry run uvicorn --app-dir apps server:app
```

View Live Feed

```bash
poetry run streamlit run apps/live_feed.py --server.headless True
```