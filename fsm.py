from transitions.extensions import GraphMachine

from utils import send_text_message,send_img_url


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, 
        **{
            "states":["user", "state1", "state2","draw"],
            "transitions":[
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
            "initial":"user",
            "auto_transitions":False,
            "show_conditions":True,}
        )

    def is_going_to_state1(self, event):
        text = event.message.text
        return text.lower() == "go to state1"

    def is_going_to_state2(self, event):
        text = event.message.text
        return text.lower() == "go to state2"

    def on_enter_state1(self, event):
        print("I'm entering state1")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state1")
        self.go_back()

    def on_exit_state1(self):
        print("Leaving state1")

    def on_enter_state2(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state2")
        self.go_back()

    def on_exit_state2(self):
        print("Leaving state2")
    def is_going_to_draw(self, event):
        text = event.message.text
        return text.lower() == "draw"

    def on_enter_draw(self, event):
        print("I'm entering draw")

        reply_token = event.reply_token
        send_img_url(reply_token, "https://raw.githubusercontent.com/yenshipotato/tocp/main/fsm.png")
        self.go_back()

    def on_exit_draw(self):
        print("Leaving draw")
