# Devoxx: Game, Set, Match: Transforming Live Sports with AI-Driven Commentary

This is the repository for a talk by Mark Needham and Dunith Danushka at Devoxx UK 2024.

https://www.devoxx.co.uk/talk/?id=11171

>We are both big fans of the live text commentary that the BBC provide for sports like football, tennis, rugby, cricket and more. While there are a lot of novel observations in the commentary, there is also a lot that is effectively summarising what just happened.
>Wouldn't it be cool if the commentator could have a Co-Pilot who can make the process more efficient?
>In this session, we will introduce an AI Co-Pilot for sports commentary based on Redpanda, ClickHouse, Flink, and a Large Language Model. A stream of events will be fed into RedPanda and we'll capture a window of those events on game-by-game and/or time-period buckets using Flink. These events, alongside historical match data, will also be stored in ClickHouse.
>We'll then send the LLM the events that have just happened along with queries on historical data, from which it can come up with suggested text commentary. The commentator can then decide whether they want to use the Co-Pilot's suggestion, edit the suggestion, or just go along with their own version.

This we need

* A stream of events related to a match
* A page that shows commentary of the match
* A page where the live commentary writer can add a new message
    ** On that page we should show the latest events and have a button to generate an AI message
    ** A way to bring in stats related to the players/tournament/etc
