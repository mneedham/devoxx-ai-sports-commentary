from kafka import KafkaProducer
from twisted.internet import task, reactor
import jsonlines
import datetime as dt
import json
import click
from functools import partial

# Timeout in seconds after which the script will exit if no new events are published
TIMEOUT_SECONDS = 60  # Example timeout period of 5 minutes

def emit_events(timeout):
    global producer, events, last_publish_time

    to_publish = [
        event 
        for event in events
        if dt.datetime.fromisoformat(event['potential_publish_time']) < dt.datetime.now() and not event["published"]
    ]
    
    for event in to_publish:
        event["publish_time"] = dt.datetime.now().isoformat()
        print(event)
        producer.send(topic="points", key=event['id'], value=event)        
        event["published"] = True
        last_publish_time = dt.datetime.now()  # Update last publish time on event publish
    producer.flush()

    # Check if the timeout has been reached
    if (dt.datetime.now() - last_publish_time).total_seconds() > timeout:
        print("Timeout reached with no new events. Exiting...")
        reactor.stop()

def cbLoopDone(result):
    print("Loop done.")
    reactor.stop()

def ebLoopFailed(failure):
    print(failure.getBriefTraceback())
    reactor.stop()

@click.command()
@click.option('--loop-frequency', default=1.0, help='Every how often should the ingestion loop run (in seconds)')
@click.option('--speed-up-factor', default=20.0, help='Event generation speedup.')
@click.option('--timeout', default=30.0, help='Timeout period.')
@click.option('--file', default="data/1602.json", help='File to ingest.')
def run(loop_frequency, speed_up_factor, timeout, file):
    global producer, events, last_publish_time

    TIMEOUT_SECONDS = timeout
    
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=str.encode
    )

    with jsonlines.open(file) as reader:
        events = [row for row in reader]

    now = dt.datetime.now()
    last_publish_time = now  # Initialize last publish time
    for event in events:
        hours, minutes, seconds = [int(value) for value in event["time"].split(":")]
        cumulative_seconds = ((60*60*hours) + (60*minutes) + seconds) / speed_up_factor
        publish_time = now + dt.timedelta(seconds = cumulative_seconds)

        event["potential_publish_time"] = publish_time.isoformat()
        event["published"] = False

    l = task.LoopingCall(partial(emit_events, timeout))
    loopDeferred = l.start(loop_frequency)
    loopDeferred.addCallback(cbLoopDone)
    loopDeferred.addErrback(ebLoopFailed)

    reactor.run()

if __name__ == "__main__":
    run()
