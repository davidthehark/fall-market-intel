import os
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from trigger_scan import send_and_wait

slack_app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)


@slack_app.event("app_mention")
def handle_mention(event, say):
    user_text = event.get("text", "")
    question = user_text.split(">", 1)[-1].strip()

    if not question:
        say("What would you like to know? Ask me anything about our market.")
        return

    response = send_and_wait(question)
    say(response)


flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    flask_app.run(host="0.0.0.0", port=port)