import os
from datetime import datetime

from flask import Flask, abort, request

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))
user_id=[]


@app.route("/", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "Hello Heroku"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def talk(event):
    if event.message.text == "靠北":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我幹你娘")
        )
    elif event.message.text == "id":
        profile = line_bot_api.get_profile(event.source.user_id)
        user_pic = profile.picture_url
        user_id = profile.user_id
        user_name = profile.display_name
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你好"+user_name))
        line_bot_api.push_message(user_id, TextSendMessage(text="你的UD是:"+user_id))
        line_bot_api.push_message(user_id, TextSendMessage(text="帥喔"))
        line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=user_pic, preview_image_url=user_pic))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

