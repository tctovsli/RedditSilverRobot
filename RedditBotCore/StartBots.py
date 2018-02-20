# Written by Rudy Pikulik 07/17

import pickle
from rocketchat_API.rocketchat import RocketChat
import time
from Structures.Queue import Queue
import RedditSilverRobot
from datetime import datetime

print("Starting up the bots!")

rocket = RocketChat('johanna', 'Passord1', server_url='http://rocketchat-rocket-chat.cluster.poc')


# This defines the domain from which to collect comments. "all" for all comments.
#sub = reddit.subreddit("all")


bots = [RedditSilverRobot]


def start_stream():
    messages = rocket.channels_history('tznw8qNDK94F3nf3u', count=10).json()  # Henter 10 siste meldinger på #bot-warz
    for comment in messages['messages']:
        for bot in bots:
            if bot.validate_comment(comment):
                queue = pickle.load(open(bot.file, 'rb'))
                if queue:
                    queue.enqueue(comment['_id'])
                else:
                    queue = Queue()
                    queue.enqueue(comment['_id'])
                pickle.dump(queue, open(bot.file, 'wb'))
                timestr = str(time.localtime()[3]) + ":" + str(time.localtime()[4])
                print("> %s - Added comment to queue! Queue length: %s" % (timestr, len(queue)))


while True:
    try:
        print('Checking the last 10 messages from now %s' % (datetime.now()))
        start_stream()
        time.sleep(5)
    except Exception as e:
        print("> %s - Connection lost. Restarting in 3 seconds... %s" % (datetime.now(), e))
        time.sleep(3)
        continue
