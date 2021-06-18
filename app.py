import os
from datetime import datetime

from flask import Flask, abort, request

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage

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
        #line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=user_pic, preview_image_url=user_pic))
    elif event.message.text == "button":
        buttons_template = TemplateSendMessage(
            alt_text='Buttons Template',
            template=ButtonsTemplate(
                title='這是ButtonsTemplate',
                text='ButtonsTemplate可以傳送text,uri',
                thumbnail_image_url='https://ibb.co/qB56zTF',
                actions=[
                    MessageTemplateAction(
                        label='ButtonsTemplate',
                        text='ButtonsTemplate'
                    ),
                    URITemplateAction(
                        label='VIDEO1',
                        uri='https://www.youtube.com/watch?v=Qn8R-kgSVRU'
                    ),
                    PostbackTemplateAction(
                        label='postback',
                        text='postback text',
                        data='postback1'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
    elif event.message.text == "YN":
        print("Confirm template")       
        Confirm_template = TemplateSendMessage(
            alt_text='目錄 template',
            template=ConfirmTemplate(
                title='這是ConfirmTemplate',
                text='這就是ConfirmTemplate,用於兩種按鈕選擇',
                actions=[                              
                    PostbackTemplateAction(
                        label='Y',
                        text='Y',
                        data='action=buy&itemid=1'
                    ),
                    MessageTemplateAction(
                        label='N',
                        text='N'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,Confirm_template)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

