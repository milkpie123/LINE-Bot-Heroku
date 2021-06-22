import os
import json
from datetime import datetime
from flask import Flask, abort, request, render_template

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
#from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))
DATABASE_URL = os.environ['DATABASE_URL']

def write_json(new_data, filename='data.json'):
    with open(filename,'r+',encoding="utf-8") as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_dat3a with file_data
        file_data.update(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)




@app.route("/", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "Hello LineBot"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"
    
@app.route("/home") #根目錄
def test():
    return render_template("cover.html")

@app.route("/forms") #根目錄
def forms():
    return render_template("forms.html")

@app.route("/sendresult", methods=["POST"])
def sendresult():
    User_name = request.form.get("User_name")
    content = request.form.get("content")
    def get_key(val):             
        for key, value in data["name_dict"].items(): 
            if val == value:
                return key
    try:
        with open('information.json','r+',encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)
            UID = get_key(User_name)
            line_bot_api.push_message(UID, TextSendMessage(text=content))
        return render_template("success.html")
    except:
        return render_template("fail.html")


    
    
@handler.add(FollowEvent)
def follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    user_pic = profile.picture_url
    user_id = profile.user_id
    user_name = profile.display_name
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="Welcome!"+user_name))
    Confirm_template = TemplateSendMessage(
            alt_text='Do U want to join with us?',
            template=ConfirmTemplate(
                title='Do U want to join with us?',
                text='Do U want to join with us?',
                actions=[
                    PostbackTemplateAction(
                        label='Yes',
                        text='Yes',
                        data='action=buy&itemid=1'),
                    MessageTemplateAction(
                        label='N0',
                        text='N0')]))
    line_bot_api.push_message(user_id, Confirm_template)    
    
    
    
    
@handler.add(MessageEvent, message=TextMessage)
def talk(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    user_pic = profile.picture_url
    user_id = profile.user_id
    user_name = profile.display_name
    
    if event.message.text == "靠北":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我幹你娘")
        )

    elif event.message.text == "Yes":
        with open('information.json','r+',encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)
            if user_id in list(data["name_dict"]):
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你已經參加了"))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="參加成功，趕快到來看看吧!"))
                line_bot_api.push_message(user_id, TextSendMessage(text='https://nccuacct-angels.herokuapp.com/home'))
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                cursor = conn.cursor()
                record = (user_id, user_name)
                table_columns = '(user_id, username)'
                postgres_insert_query = f"""INSERT INTO account {table_columns} VALUES (%s, %s);"""
                cursor.execute(postgres_insert_query, record)
                conn.commit()
                cursor.close()
                conn.close()
                
    elif event.message.text == "No":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="OK, remember U can join anytime u want~"))


    elif event.message.text == "id":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你好"+user_name))
        line_bot_api.push_message(user_id, TextSendMessage(text="你的User ID是:"+user_id))
        line_bot_api.push_message(user_id, TextSendMessage(text="帥喔"))
        #line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=user_pic, preview_image_url=user_pic))
        
        
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="Anything?"))
    '''
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
                        label='開始填寫',
                        uri='https://nccuacct-angels.herokuapp.com/home'
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
        #print("Confirm template")       
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
   
    elif event.message.text == "姓名":
            user_name = event.message.text
            Confirm_template = TemplateSendMessage(
                alt_text='目錄 template',
                template=ConfirmTemplate(
                    title='你確定這是你的姓名嗎?',
                    text='別打錯字拜託',
                    actions=[                              
                        PostbackTemplateAction(
                            label='Yes',
                            text='Yes',
                            data='action=buy&itemid=1'
                        ),
                        MessageTemplateAction(
                            label='N0',
                            text='N0'
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token,Confirm_template)
  
    elif event.message.text == "Yes":
        write_json({user_id:user_name})
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="參加成功"))
     '''    
