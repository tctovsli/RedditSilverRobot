# Created by Rudy Pikulik 04/17
# Last Updated 12/17
import pickle
import time
from Structures.Queue import Queue
from rocketchat_API.rocketchat import RocketChat

rocket = RocketChat('johanna', 'Passord1', server_url='http://rocketchat-rocket-chat.cluster.poc')

file = 'RSRQueue.p'
msg_reaction = ':moneybag:'
banned_subs = [""]

def validate_comment(message):
#    print(message)
    if 'reactions' in message:
        if msg_reaction in message['reactions']:
 #           poster = message['reactions'][msg_reaction]['usernames']
 #           msg_text = message['msg']
 #           print("Message ID %s had the emoji %s on the following message: %s" % (message['_id'], message['reactions'], message['msg']))
            queue = pickle.load(open(file, "rb"))
            if not queue:
               queue = Queue()
            data = pickle.load(open('RSRData.p', 'rb'))
            # Already in the queue, don't add.
            if queue.contains(message['_id']) or message['_id'] in [x[0] for x in data]:
                return False
            if message['reactions'][msg_reaction]['usernames'][0] == get_receiver(message):
                _register_comment(message, "Cannot respond to self.")
                return False
            return True
        return False
    return False

    # Decides whether or not to reply to a given comment.
    #    - Must contain command
    #    - Must not have already replied
    #    - Must not reply to self
    # if user_reaction in comment.body.lower():
    #     queue = pickle.load(open(file, "rb"))
    #     if not queue:
    #         queue = Queue()
    #     data = pickle.load(open('RSRData.p', 'rb'))
    #     # Already in the queue, don't add.
    #     if queue.contains(comment.id) or comment.id in [x[0] for x in data]:
    #         return False
    #     # We wrote the comment, don't loop.
    #     if comment.author.name is "RedditSilverRobot":
    #         _register_comment(comment, "Cannot respond to self.")
    #         return False
    #     # Parent comment was deleted, don't respond.
    #     if get_receiver(comment) == '[deleted]':
    #         _register_comment(comment, "Parent comment was deleted!")
    #         return False
    #     # We've blacklisted this sub, don't respond.
    #     if comment.subreddit.display_name.lower() in banned_subs:
    #         _register_comment(comment, "Subreddit is blacklisted!")
    #         return False
    #
    #     comment.refresh()
    #     for child_comment in comment.replies:
    #         if child_comment.author.name == "RedditSilverRobot":
    #             _register_comment(comment, "Already replied to this comment. Will not do it again.")
    #             return False
    #     return True
    # return False


def reply(comment):
    # Makes a message and replies to the given comment.
    reply_message = _make_message(comment)
    timestr = str(time.localtime()[3]) + ":" + str(time.localtime()[4])
    try:
        rocket.chat_post_message(reply_message, channel='GENERAL', alias='Botstøtte', avatar='http://marisa-hamanako.com/wp-content/uploads/2017/02/adult-top-coin-coloring-pages-gallery-images-dashah-beauty-quarter-coin-coloring-page-1.jpg')
        print("> %s - Posted: %s -> " % (timestr, comment['u']['username']) + get_receiver(comment))
        _register_comment(comment, "Posted!")
    except Exception as comment_exception:
        print("> %s - Unable to post comment: %s -> " % (timestr, comment['reactions'][msg_reaction]['usernames'][0]) + get_receiver(comment) + "Reason: %s" % comment_exception)
        _register_comment(comment, "Unable to post. Reason: %s" % comment_exception)


def _register_comment(comment, result):
    # Stores data in a list of tuples
    # (ID, (User, Receiver, Time, Result))
    tup = (comment['_id'], (comment['reactions'][msg_reaction]['usernames'][0], get_receiver(comment), time.localtime(), result))
    data = pickle.load(open("RSRData.p", 'rb'))
    if data:
        data.append(tup)
    else:
        data = [tup]
    pickle.dump(data, open("RSRData.p", 'wb'))


def get_receiver(message):
    return message['u']['username']

def _silver_counter(comment):
    data_entries = pickle.load(open('RSRData.p', 'rb'))
    count = 0
    if data_entries:
        receiver = get_receiver(comment)
        for entry in [x[1][1] for x in data_entries]:
            if entry == receiver:
                count += 1
        return count+1
    else:
        return 1


def _make_message(comment):
    giver_name = rocket.users_info(username=comment['reactions'][msg_reaction]['usernames'][0]).json()['user']['name']
    silver_count = _silver_counter(comment)
    if silver_count == 1:
        s = ""
    else:
        s = "s"
    message = "Hei, @" + get_receiver(comment)
    message += "! \n"
    message += str(giver_name) + " har gitt deg HBcoin. Du har til sammen " + str(silver_count)
    message += " HBcoin%s." % s
    #message += comment['reactions'][msg_reaction]['usernames'][0] + ") "
    #message += "__[info](http://reddit.com/r/RedditSilverRobot)__" + comment.subreddit.display_name
    return message

if __name__ == '__main__':

    try:
        queue = pickle.load(open(file, "rb"))
    except EOFError and FileNotFoundError as e:
        print("queue startup: %s" % e)
        queue = Queue()
        pickle.dump(queue, open(file, 'wb'))

    try:
        __data = pickle.load(open("RSRData.p", "rb"))
    except EOFError and FileNotFoundError:
        __data = []
        pickle.dump(__data, open("RSRData.p", 'wb'))
    if __data:
        print("There are %s entries in data." % len(__data))
    else:
        print("Data is empty.")
    if queue:
        print("There are %s entries in the queue." % len(queue))
    else:
        print("Queue is empty.")
    while True:
        try:
            queue = pickle.load(open(file, 'rb'))
        except EOFError:
            queue = Queue()
        if queue and len(queue) > 0:
            comment_id = queue.dequeue()
            pickle.dump(queue, open(file, 'wb'))
            message = rocket.chat_get_message(comment_id).json()['message']
            reply(message)
        time.sleep(3)
