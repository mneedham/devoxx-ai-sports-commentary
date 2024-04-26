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


CREATE TABLE matches
ORDER BY match_id AS
SELECT * REPLACE(
    toString(match_id) AS match_id
)
FROM file('matches.csv') 
SETTINGS schema_inference_make_columns_nullable=0;

-- {
-- "id":"set3_game_13_point_201"
-- "time":"2:40:36"
-- "player1":"B. Shelton"
-- "player2":"N. Djokovic"
-- "previous_sets":[
-- 0:"3 - 6"
-- 1:"2 - 6"
-- ]
-- "server":"N. Djokovic"
-- "set":"3"
-- "game":"tiebreak"
-- "set_score":"6 - 7 (4-7)"
-- "point_score":"FINISH"
-- "description":"B. Shelton loses the match with a forehand forced error"
-- "game_winner":"N. Djokovic"
-- "potential_publish_time":"2024-04-18T13:46:46.952932"
-- "published":false
-- "publish_time":"2024-04-18T13:46:47.155867"
-- }