import os
from random import randint
import pandas as pd
import psycopg2
from flask import Flask, abort, request, render_template

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
#from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))
DATABASE_URL = os.environ.get("DATABASE_URL")


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
def home():
    return render_template("cover.html")

@app.route("/forms", methods=['GET']) #根目錄
def forms():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    sql = "select * from account;"
    dat = pd.read_sql_query(sql, conn)
    conn = None
    table = zip(dat["user_id"], dat["username"])
    return render_template("forms.html", table=table)

@app.route("/sendresult", methods=["POST"])
def sendresult():
    try:
        UID = request.form.get("UID")
        content = request.form.get("content")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        record = (UID, content)
        table_columns = '(user_id, comment)'
        query1 = f"""INSERT INTO temp_comments {table_columns} VALUES (%s, %s);"""
        query2 = f"""INSERT INTO permanent_comments {table_columns} VALUES (%s, %s);"""
        cursor.execute(query1, record)
        cursor.execute(query2, record)
        conn.commit()
        cursor.close()
        conn.close()
        return render_template("success.html")
    except:
        return render_template("fail.html")
    #try:
        #line_bot_api.push_message(UID, TextSendMessage(text=content))
        #return render_template("success.html")
    #except:
        #return render_template("fail.html")

@app.route("/youshouldneverbehere") #集中發送訊息，寄完刪掉
def youshouldneverbehere():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        sql = "select * from temp_comments;"
        dat = pd.read_sql_query(sql, conn)
        for x,y in zip(dat["user_id"], dat["comment"]):
            try:
                line_bot_api.push_message(x, TextSendMessage(text=y))
            except:
                pass
        cur = conn.cursor()
        cur.execute("delete from temp_comments;")
        conn.commit()
        cur.close()
        conn.close()
        return "Finish :)"
    except:
        return "Error :("

    
@handler.add(FollowEvent)
def follow(event):
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
        user_id = profile.user_id
        user_name = profile.display_name
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        record = (user_id, user_name)
        table_columns = '(user_id, username)'
        postgres_insert_query = f"""INSERT INTO account {table_columns} VALUES (%s, %s);"""
        cursor.execute(postgres_insert_query, record)
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass 
    
@handler.add(MessageEvent, message=TextMessage)
def talk(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    #user_pic = profile.picture_url
    user_id = profile.user_id
    user_name = profile.display_name
    
    if event.message.text == "加入":
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()
            record = (user_id, user_name)
            table_columns = '(user_id, username)'
            postgres_insert_query = f"""INSERT INTO account {table_columns} VALUES (%s, %s);"""
            cursor.execute(postgres_insert_query, record)
            conn.commit()
            cursor.close()
            conn.close()
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="參加成功，趕快去玩看看吧！"))
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="參加成功，趕快去玩看看吧！"))
                
    elif event.message.text == "退出":
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM account WHERE user_id = '%s';" %user_id)
            conn.commit()
            cursor.close()
            conn.close()
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你不會再收到訊息(除了今天已經填寫的)，你可以隨時輸入「加入」重新參與。"))
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你不會再收到訊息(除了今天已經填寫的)，你可以隨時輸入「加入」重新參與。"))

    else:
        n = randint(0,13)
        if n == 0:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="誰是報告特別carry的神隊友？"))
        elif n == 1:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="誰是幹話大王？"))
        elif n == 2:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="誰是跟你莫名其妙就變熟的？"))
        elif n == 3:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你大學認識的第一個人是誰？"))
        elif n == 4:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你知道會計五帥嗎？"))
        elif n == 5:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你最喜歡的系上活動是什麼？"))
        elif n == 6:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="誰都不去上課？"))
        elif n == 7:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="誰都說自己沒讀書但還是考很好？"))
        elif n == 8:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你覺得大學4年誰改變最多？"))
        elif n == 9:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你覺得系上誰最熱心助人？"))
        elif n == 10:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="誰是專門搞事的雷組員？"))
        elif n == 11:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="誰有深藏不漏的特殊才藝？"))
        elif n == 12:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="還沒跟誰好好道別/說謝謝嗎？"))
        elif n == 13:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="誰特別難揪？"))
        

   
'''
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
                    label='No',
                    text='No')]))
line_bot_api.reply_message(event.reply_token,Confirm_template)    
'''
'''
    if event.message.text == "靠北":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我幹你娘")
        )

    elif event.message.text == "Yes":
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        sql = "select * from account;"
        dat = pd.read_sql_query(sql, conn)
        if user_id in dat["user_id"].tolist():
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你已經參加囉，趕快去看看吧！"))
            #line_bot_api.push_message(user_id, TextSendMessage(text='https://nccuacct-angels.herokuapp.com/home'))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="參加成功，趕快來看看吧！"))
            #line_bot_api.push_message(user_id, TextSendMessage(text='https://nccuacct-angels.herokuapp.com/home'))
            cursor = conn.cursor()
            record = (user_id, user_name)
            table_columns = '(user_id, username)'
            postgres_insert_query = f"""INSERT INTO account {table_columns} VALUES (%s, %s);"""
            cursor.execute(postgres_insert_query, record)
            conn.commit()
            cursor.close()
            conn.close()    


    elif event.message.text == "id":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你的User ID是:"+user_id))
        #line_bot_api.push_message(user_id, TextSendMessage(text="你的User ID是:"+user_id))
        #line_bot_api.push_message(user_id, TextSendMessage(text="帥喔"))
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

