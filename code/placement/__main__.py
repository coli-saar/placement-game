from collections import defaultdict
import logging
import random
from threading import Timer
import string
import requests
from time import sleep
from templates import TaskBot
from random import randrange, choice


from .config import *
from .msgfunctions import *

class RoomTimer:
    def __init__(self, function, room_id, TIMER):
        self.function = function
        self.room_id = room_id
        self.start_timer(TIMER)

    def start_timer(self, TIMER):
        self.timer = Timer(
            TIMER*60,
            self.function,
            args=[self.room_id]
        )
        self.timer.start()

    def reset(self, TIMER):
        self.timer.cancel()
        self.start_timer(TIMER)
        logging.debug("reset timer")

    def cancel(self):
        self.timer.cancel()


class Session:
    def __init__(self):
        self.players = list()
        self.timer = RoomTimer
        self.halfway_timer = RoomTimer
        self.one_minute_timer = RoomTimer
        self.latest_board = dict()
        self.new_board = list()
        self.counter = 1  # number of rounds to play; the actual number is n+1
        self.submissions = set()
        self.scores = list()

    def close(self):
        self.timer.cancel()


class SessionManager(defaultdict):
    def create_session(self, room_id):
        self[room_id] = Session()

    def clear_session(self, room_id):
        if room_id in self:
            self[room_id].close()
            self.pop(room_id)


class Placement(TaskBot):

    session_manager = SessionManager(Session)
    data_collection = "AMT"

    def on_task_room_creation(self, data): # NOTE: this function does not work?
        room_id = data["room"]

        # automatically creates a room if it does not exists (defaultdict)
        this_session = self.session_manager[room_id]
        this_session.timer = RoomTimer(
            self.close_room_timeout, room_id, TIMEOUT_TIMER
        )
        this_session.halfway_timer = RoomTimer(
            self.warning_timer_half, room_id, TIMEOUT_TIMER//2
        )

        this_session.one_minute_timer = RoomTimer(
            self.warning_timer_one_min, room_id, TIMEOUT_TIMER-1
        )

        # add users to this session
        for usr in data["users"]:
            this_session.players.append(usr)

            # map a dictionary user_id: last board
            this_session.latest_board[usr["id"]] = None

        # manually adding the LLM bot
        LLM_bot_user = {'id':000, 'name':"BOT"}
        this_session.players.append(LLM_bot_user)

        # [{'name': 'pillow', 'x': 642, 'y': 548}, {'name': 'garbage', 'x': 418, 'y': 281}, {'name': 'cap', 'x': 667, 'y': 502}, {'name': 'cowboy', 'x': 657, 'y': 518}, {'name': 'pants', 'x': 368, 'y': 618}]

        logging.debug(f"USERS: {this_session.players}, usr: {usr}")

        self.move_divider(room_id, chat_area=25, task_area=75) # resize chat area

    def warning_timer_half(self, room_id):

        # message - There are 6 minutes left of this round.
        self.sio.emit(
            "text",
            {
                "message": COLOR_MESSAGE.format(
            color=WARNING_COLOR,
            message=f"Halfway done. There are {TIMEOUT_TIMER//2} minutes left.",
            ),
                "room": room_id,
                "html": True
            },
        )

    def warning_timer_one_min(self, room_id):

        self.sio.emit(
            "text",
            {
                "message": COLOR_MESSAGE.format(
            color=WARNING_COLOR,
            message="Only 1 minute left! Please submit your solution to proceed!",
            ),
                "room": room_id,
                "html": True
            },
        )

    def close_room(self, room_id):
        self.room_to_read_only(room_id)

        # delete data structures
        self.session_manager.clear_session(room_id)

    def close_room_timeout(self, room_id):
        
        # the messages including the unique ID to be copied to the survey
        self.sio.emit(
            "text",
            {
                "message": COLOR_MESSAGE.format(
            color=WARNING_COLOR,
            message="You took too long and were disconnected. Please paste the following code into Prolific: C10AVA0Z",
            ),
                "room": room_id,
                "html": True
            },
        )
        self.room_to_read_only(room_id)

        # delete data structures
        self.session_manager.clear_session(room_id)

    def calculate_score(self, board1, board2):

        ''' A function calculating the score based on the given object placement on two boards.
        
        :param board1: list of dicts
        :param board2: list of dicts
        
        :return score: int
        
        '''

        # sort the boards by name of object
        sorted1 = sorted(board1, key=lambda d: d.get("name"), reverse=True)
        sorted2 = sorted(board2, key=lambda d: d.get("name"), reverse=True)

        scores = {} # k: obj, v: score

        for obj1, obj2 in zip(sorted1, sorted2): # ob1, ob2 --> dicts
            object = obj1['name']
            ManhattanDistance = abs( obj1['x'] - obj2['x'] ) + abs( obj1['y'] - obj2['y'] )

            scores[object] = ManhattanDistance
        
        if set(scores.values()) == set([0]):
            return 100
        
        else:
            # max x = 1240; max y = 816; maxdist = 2056
            # max x = 1024; max y = 740; maxdist = 1764
            max_dist = 1764
            percent_off = []
            for score in scores.values():
                percent = score * 100 / max_dist
                percent_off += [percent]
                
            avg_percent_off = sum(percent_off) / len(percent_off)
            final_score = round(100 - avg_percent_off, 2)

            return final_score

    def confirmation_code(self, room_id, bonus, receiver_id=None):
        """ Generate token that will be sent to each player. """
        kwargs = dict()
        # either only for one user or for both
        if receiver_id is not None:
            kwargs["receiver_id"] = receiver_id

#        confirmation_token = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

        if bonus:
            confirmation_token = "BONUSCODE"
        else:
            confirmation_token = "REGULARCODE"

        # post confirmation token to logs
        response = requests.post(
            f"{self.uri}/logs",
            json={
                "event": "confirmation_log",
                "room_id": room_id,
                "data": {"confirmation_token": confirmation_token},
                **kwargs,
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.request_feedback(response, "post confirmation token to logs")

        self._show_amt_token(room_id, confirmation_token, receiver_id)

        return confirmation_token

    def _show_amt_token(self, room, token, receiver):

        # the messages including the unique ID to be copied to the survey
        self.sio.emit(
            "text",
            {
                "message": COLOR_MESSAGE.format(
            color=STANDARD_COLOR,
            message="Please copy the following unique ID code before you close this window and go back to Prolific.",
            ),
                "room": room,
                "html": True
            },
        )

        self.sio.emit(
            "text",
            {
                "message": COLOR_MESSAGE.format(
                    color=STANDARD_COLOR, message=f"Your confirmation code: {token}"
                ),
                "room": room,
                "receiver_id": receiver,
                "html": True
            },
        )


    def register_callbacks(self):
        
        @self.sio.event
        def joined_room(data):
            """Triggered once after the bot joins a room."""
            logging.debug('WE HAVE ENTERED THE ROOM')
            logging.debug(f'DATA:\t{data}')
            room_id = data["room"]
            if room_id:
                logging.info(f"Bot joined room {room_id}")
            else:
                logging.error("No room_id provided in joined_room data")

            # user_id = data["user"]["id"]
            # other_user = [usr for usr in self.users_global if usr != user_id]

            # read out task greeting
            lines = ["*Welcome to the placement game!*",
                     "--------------------------------",
                     """You and your partner are seeing the same room and the same objects.
                     The objects, however, are placed in different positions. 
                     **THE GOAL** is for both you and your partner to have the objects placed in *the same position*. The objects cannot overlap. 
                     You can communicate through the chat; use English only.""",
                     "When you're done, **YOU** need to click the submit button.",
                     "*NOTE*: before you start, make sure to **resize your chat** so that the entire image on the right and all three objects are visible. (it's recommended to resize it until you see a gray border on the right) You might have to zoom out (CTRL+- or CMD+-) of your browser view so that the entire image fits.",
                     "*NOTE*: If your partner leaves before you completed the experiment, please contact the researcher on Prolific immediately.",
                     "--------------------------------"]

            for line in lines:
                
                self.sio.emit(
                    "text",
                    {
                        "message": WELCOME.format(
                            message=line, color=STANDARD_COLOR
                        ),
                        "room": room_id,
                        "html": True
                    },
                )
 
        @self.sio.event
        def text_message(data):
                        
            if self.user == data["user"]["id"]:
                return
            else:
                room_id = data["room"]

            logging.debug(f"message received")

            this_session = self.session_manager[room_id]

            # logging.debug(f'THIS SESSION:\t{this_session}')
            self.log_event("board_logging", {"board": this_session.latest_board}, room_id) # log the bot's changes to log files

            logging.debug(this_session.latest_board)

        @self.sio.event
        def command(data):
            """Parse user commands."""
            room_id = data["room"]
            user_id = data["user"]["id"]

            # do not process commands from itself
            if user_id == self.user:
                return

            logging.debug(
                f"Received a command from {data['user']['name']}: {data['command']}"
            )

            this_session = self.session_manager[room_id]

            if isinstance(data["command"], dict):
                # if the command is a dict (currently: only board_logging)
                if data["command"]["event"] == "board_logging":
                    board = data["command"]["board"]
                    # update latest board for this user
                    this_session.latest_board[user_id] = board
                    logging.debug(this_session.latest_board)

            else:
                if data["command"] == "stop":
                    # retrieve latest board and calculate score
                    board1, board2 = list(this_session.latest_board.values())
                    score = self.calculate_score(board1, board2)

                    # log extra event (score event)
                    self.log_event("score", {"score": score}, room_id)
                    self.log_event("board_logging", {"board": this_session.latest_board}, room_id)

                    this_session.timer.reset(TIMEOUT_TIMER)
                    this_session.halfway_timer.reset(TIMEOUT_TIMER/2)
                    this_session.one_minute_timer.reset(TIMEOUT_TIMER-1)

                    this_session.scores += [score] # add the score to the list of scores

                    this_session.submissions = set() # empty the list of who submitted (for next round)

                    if this_session.counter == 0: # if this is the last round
                        
                        # Inform users the experiment is over and give them the last score
                        msg = f"Your score is {score}. Thank you for playing! Please wait for your unique ID token."
                        self.sio.emit(
                            "text",
                            {
                                "message": COLOR_MESSAGE.format(message=msg, color=SUCCESS_COLOR),
                                "room": room_id,
                                "html": True,
                            },
                        )

                        bonus = any(el >= 99 for el in this_session.scores)

                        # Generating and showing the AMT token
                        for usr in this_session.players:
                            self.confirmation_code(room_id=room_id, bonus=bonus, receiver_id=usr["id"])

                        self.close_room(room_id)

                    else: # if there's more rounds to play
                        this_session.counter -= 1
                        msg = f"Your score is {score}. The round is over. Please wait for the next round to start."

                        self.sio.emit(
                            "text",
                            {
                                "message": COLOR_MESSAGE.format(message=msg, color=SUCCESS_COLOR),
                                "room": room_id,
                                "html": True,
                            },
                        )

                        sleep(0.5)

                        # run the new_episode command from the js pluging (placement.js); for resetting the front-end
                        self.sio.emit(
                            "message_command",
                            {
                                "command": {
                                    "event": "new_episode"
                                },
                                "room": room_id,
                            },
                        )

    def room_to_read_only(self, room_id):
        """Set room to read only."""
        # set room to read-only
        response = requests.patch(
            f"{self.uri}/rooms/{room_id}/attribute/id/text",
            json={"attribute": "readonly", "value": "True"},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if not response.ok:
            logging.error(f"Could not set room to read_only: {response.status_code}")
            response.raise_for_status()

        response = requests.patch(
            f"{self.uri}/rooms/{room_id}/attribute/id/text",
            json={"attribute": "placeholder", "value": "This room is read-only"},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if not response.ok:
            logging.error(f"Could not set room to read_only: {response.status_code}")
            response.raise_for_status()

        response = requests.get(
            f"{self.uri}/rooms/{room_id}/users",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if not response.ok:
            logging.error(f"Could not get user: {response.status_code}")

        users = response.json()
        for user in users:
            if user["id"] != self.user:
                response = requests.get(
                    f"{self.uri}/users/{user['id']}",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                if not response.ok:
                    logging.error(f"Could not get user: {response.status_code}")
                    response.raise_for_status()
                etag = response.headers["ETag"]

                response = requests.delete(
                    f"{self.uri}/users/{user['id']}/rooms/{room_id}",
                    headers={"If-Match": etag, "Authorization": f"Bearer {self.token}"},
                )
                if not response.ok:
                    logging.error(
                        f"Could not remove user from task room: {response.status_code}"
                    )
                    response.raise_for_status()
                logging.debug("Removing user from task room was successful.")

if __name__ == "__main__":
    # set up loggingging configuration
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")

    # create commandline parser
    parser = Placement.create_argparser()
    args = parser.parse_args()

    # create bot instance
    bot = Placement(args.token, args.user, args.task, args.host, args.port)
    # connect to chat server
    bot.run()
