import pickle
import time
from Structures.Queue import Queue
from rocketchat_API.rocketchat import RocketChat
from pprint import pprint

rocket = RocketChat('johanna', 'Passord1', server_url='http://rocketchat-rocket-chat.cluster.poc')

messages = rocket.channels_history('tznw8qNDK94F3nf3u',count=10).json() # Henter 10 siste meldinger på #bot-warz
msg_reaction = ':grinning:'

for message in messages['messages']:
        if 'reactions' in message:
            if msg_reaction in message['reactions']:
                poster = message['reactions'][msg_reaction]['usernames']
                msg_text = message['msg']
                print("User %s used the emoji %s on the following message: %s" % (poster,msg_reaction, msg_text))
