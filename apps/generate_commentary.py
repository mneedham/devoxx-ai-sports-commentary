from openai import OpenAI
import jsonlines

client = OpenAI()

system_message = """
You're the assistant or copilot to a person who's writing live-text updates for a tennis match. 
You'll receive a list of events describing what's happened and you need to come up with a one or two-sentence summary based on that data. 
Pull out things that you think are interesting including the length of the game if it's very short or long, shots on important points, and so on.
Write in the present tense and in a way that's accessible to your average tennis fan.
"""

def call_llm(events, model="gpt-4", stream=True):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
            "role": "system",
            "content": system_message
            },
            {
            "role": "user",
            "content": "\n".join([str(item) for item in events])
            }
        ],
        stream=stream
    )
    return response


if __name__ == "__main__":
    with jsonlines.open('data/events.json') as reader:
        events = [row for row in reader]

    events_by_game = []
    game = []
    for event in events:
        game.append(event)
        if event['point_score'] == 'FINISH':
            events_by_game.append(game)
            game = []

    # response = call_llm(events_by_game[10])
    # for chunk in response:
    #     print(chunk.choices[0].delta.content or "", end='', flush=True)

    response = call_llm(events_by_game[10], stream=False, model="gpt-3.5-turbo")
    print(response.choices[0].message.content)