score_query = """
SELECT
    matches.* EXCEPT(match_id),
    latestPoint.previous_sets,
    set_score,
    point_score
FROM matches
LEFT JOIN
(
    SELECT *
    FROM points
    WHERE match_id = %(match_id)s
    ORDER BY id DESC
    LIMIT 1
) AS latestPoint ON latestPoint.match_id = matches.match_id
WHERE match_id = %(match_id)s
"""

latest_game_query = """
SELECT points.* EXCEPT (match_id, id, publish_time)
FROM points
INNER JOIN
(
    SELECT *
    FROM points
    WHERE (point_score = 'FINISH') AND (match_id = %(match_id)s)
    ORDER BY id DESC
    LIMIT 1
) AS latestPoint ON (latestPoint.set = points.set) AND (latestPoint.game = points.game)
WHERE match_id = %(match_id)s
ORDER BY id
"""