import os
import sys
import json

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,ImageSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()

machine = TocMachine(
    states=["user", "state1", "state2","draw"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state1",
            "conditions": "is_going_to_state1",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state2",
            "conditions": "is_going_to_state2",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "draw",
            "conditions": "is_going_to_draw",
        },
        {"trigger": "go_back", "source": ["state1", "state2","draw"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)
machines={}

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

def handleTrigger(state, events, user_id):
    print("Server Handling State : %s" % state)
    if state == "user":
        machines[user_id].advance(events)

@app.route('/callback', methods=['GET'])
def reply():
    return 'Hello, World!'

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        res = json.loads(body)
        print(type(res))
        user_id=res["events"][0]["source"]["userId"]
        if user_id not in machines:
            machines[user_id] = TocMachine()
        handleTrigger(machines[user_id].state, event, user_id)

    return "OK"
    '''
    webhook = json.loads(request.data.decode("utf-8"))
    reply_token, user_id, message = webhook_parser(webhook)
    print(reply_token, user_id, message)

    

    handleTrigger(machines[user_id].state, reply_token, user_id, message)
    return jsonify({})'''



@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    TocMachine().get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
