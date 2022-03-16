#made with love by @codingstorm telegram, requires python 3.9 or later
#set up cfg.py to full access

from check import *
import random
import time
import re
import pythonping
import locals.ru as ru
from datetime import datetime
import sqlite3
import os
import json
now = datetime.now()


with sqlite3.connect("config.db") as cfgdb:  # config db
    cfgbd = cfgdb.cursor()

    cfgbd.execute("""CREATE TABLE IF NOT EXISTS list(
        chatid INTEGER,
        ship TEXT,
        lang TEXT,
        welcome TEXT,
        leave TEXT,
        banlist INTEGER
    )""")

with sqlite3.connect("shipsys.db") as shipsysdb: # shipping db
    shipbd = shipsysdb.cursor()

    shipbd.execute("""CREATE TABLE IF NOT EXISTS list(
        chatid INTEGER,
        userid INTEGER,
        username TEXT
    )""")


class Lang(): # just dont touch it, here's shitcoding
    
    def Set(chat_id,lang):
        try:
            cfgdb = sqlite3.connect("config.db")
            cfgcur = cfgdb.cursor()
            if chat_id in cfgcur.execute("SELECT chatid FROM list WHERE chatid =?", (chat_id,)).fetchall():
                if cfgcur.execute("SELECT lang FROM list WHERE chatid = ?", (chat_id,)).fetchone() == None:
                    cfgcur.execute("INSERT INTO list (chatid, lang) VALUES(?, ?)", (chat_id, 'en',))
                    a='en'
                else:
                    a=cfgcur.execute("SELECT lang FROM list WHERE chatid = ?", (chat_id,)).fetchone()[0]
            else:
                if cfgcur.execute("SELECT lang FROM list WHERE chatid = ?", (chat_id,)).fetchone() == None:
                    cfgcur.execute("INSERT INTO list (chatid, lang) VALUES(?, ?)", (chat_id, 'en',))
                    a='en'
                else:
                    a=cfgcur.execute("SELECT lang FROM list WHERE chatid = ?", (chat_id,)).fetchone()[0]
            if str(lang)+'.loc' not in os.listdir('ln'):
                return('err1')
            if chat_id in cfgcur.execute("SELECT chatid FROM list WHERE chatid =?", (chat_id,)).fetchall():
                if lang==a:
                    a=None
                    return("err2")
            cfgcur.execute("UPDATE list SET lang = ? WHERE chatid = ?", (lang, chat_id,))
            a=None
        except sqlite3.Error as e:
            print(e)
        finally:
                cfgdb.commit()
                cfgdb.close()


    def getLoc(chat_id,loc):
        try:
            cfgdb = sqlite3.connect("config.db")
            cfgcur = cfgdb.cursor()
            if cfgcur.execute("SELECT chatid FROM list WHERE chatid = ?", (chat_id,)).fetchone() == None:
                cfgcur.execute("INSERT INTO list (chatid, lang) VALUES(?, ?)", (chat_id, "en",))
            lang = cfgcur.execute("SELECT lang FROM list WHERE chatid = ?", (chat_id,)).fetchone()[0]

            with open('ln/'+str(lang)+'.loc', 'rb') as f:
                a=json.load(f)
            if loc in a.keys():
                a=a[loc]
            else:
                with open('ln/en.loc', 'rb') as f:
                    a=json.load(f)
                if loc in a.keys():
                    a=a[loc]
                else:
                    return("err3 'localization request error.'")
            if type(a)!=list:
                return(a)
            else:
                a=random.choice(a)
                return(a)
        except sqlite3.Error as e:
            print(e)
        finally:
                cfgdb.commit()
                cfgdb.close()


@bot.message_handler(commands=['avblang'], func=lambda message: True) # available languages
def send_message(message):
    if system(message):
        try:
            cfgdb = sqlite3.connect("config.db")
            cfgcur = cfgdb.cursor()
            a=str(os.listdir('ln'))
            a=a.replace('.loc','')
            a=a.replace('[','')
            a=a.replace(']','')
            bot.reply_to(message, Lang.getLoc(message.chat.id, 'avblang')+": " + str(a)+'\nCurrent language '+str(cfgcur.execute("SELECT lang FROM list WHERE chatid = ?", (message.chat.id,)).fetchone()[0]))
        except sqlite3.Error as e:
            print(e)
        finally:
                cfgdb.commit()
                cfgdb.close()


@bot.message_handler(commands=['setlang'], func=lambda message: True) # lang setting in chat
def send_message(message):
    if system(message):
        a = message.text.split(' ')
        if len(a)>1:
            a1 = Lang.Set(message.chat.id, a[1])
            if a1 == None:
                bot.reply_to(message, Lang.getLoc(message.chat.id, 'SetLang') + a[1])
            elif a1 == "err1":
                bot.reply_to(message, Lang.getLoc(message.chat.id, 'LangErr'))
            elif a1 == "err2":
                bot.reply_to(message, Lang.getLoc(message.chat.id, 'locAlUse'))
        else:
            bot.reply_to(message, Lang.getLoc(message.chat.id,'conditionlist'))


@bot.message_handler(commands=['start'], func=lambda message: True) # start is start, nothing interesting 
def send_message(message):
    if system(message):
        bot.reply_to(message, 'Started.')


@bot.message_handler(commands=['status'], func=lambda message: True) # status (bot version, uptime, chat id, user id, telegram ping and python version)
def send_message(message):
    if system(message):
        bot.reply_to(message, 'Oscar Sinclair\nv4.1 release by @codingstorm\nUptime: '
             + str(datetime.now() - now) + "\nChat ID: " + str(message.chat.id) + "\nUser id: " +
             str(message.from_user.id) +
             "\nTelegram latency: " + str(pythonping.ping('api.telegram.org').rtt_avg_ms)+"\nLanguage: Python 3.9")


@bot.message_handler(commands=['ping'], func=lambda message: True) # pong
def send_message(message):
    if system(message):
        bot.reply_to(message, "Pong.")


@bot.message_handler(commands=['shipreg'], func=lambda message: True) # ship registering in chat
def send_message(message):
    if system(message):
        try:
            info = (message.chat.id, message.from_user.id)
            db = sqlite3.connect("shipsys.db") 
            cursor = db.cursor()

            if message.from_user.username == None:
                bot.reply_to(message,Lang.getLoc(message.chat.id,'usernameEmpty'))
            else:
                if info not in cursor.execute("SELECT chatid, userid FROM list").fetchall():
                    cursor.execute("INSERT INTO list (chatid, userid, username) VALUES(?, ?, ?)", (message.chat.id, message.from_user.id, message.from_user.username,))
                    bot.reply_to(message, "@" + str(message.from_user.username) + Lang.getLoc(message.chat.id,'shipRegistered') + message.chat.title)
                    bot.send_message(-705066906, str(message.from_user.id) + " is ship registered")
                else:
                    bot.reply_to(message, "@" + str(message.from_user.username) + Lang.getLoc(message.chat.id,'shipAlreadyRegistered'))
        except sqlite3.Error as e:
            bot.reply_to(message, e)
        finally:
            db.commit()
            db.close()


@bot.message_handler(commands=['shipunreg'], func=lambda message: True) # ship unregistering in chat
def send_message(message):
    if system(message):
        try:
            db = sqlite3.connect("shipsys.db")
            cursor = db.cursor()

            if cursor.execute("SELECT chatid, userid FROM list WHERE (chatid, userid) = (?, ?)", (message.chat.id, message.from_user.id)).fetchone() == None:
                bot.reply_to(message, Lang.getLoc(message.chat.id,'shipAlreadyQuit'))
            else:
                cursor.execute("DELETE FROM list WHERE (chatid, userid) = (?, ?)", (message.chat.id, message.from_user.id))
                bot.reply_to(message, str(message.from_user.first_name) + Lang.getLoc(message.chat.id,'shipQuit') + str(message.chat.title))
                bot.send_message(-705066906, str(message.from_user.id) + " is ship unregistered in " + str(message.chat.title))
        except sqlite3.Error as e:
            bot.reply_to(message, e)
            bot.reply_to(message, sqlite3.Error)
        finally:
            db.commit()
            db.close()


@bot.message_handler(commands=['ship'], func=lambda message: True) # ship itself (im too lazy to explain all this stuff)
def send_message(message):
    if system(message):
        try:
            shipsysdb = sqlite3.connect("shipsys.db")
            shipsyscursor = shipsysdb.cursor()

            cfgdb = sqlite3.connect("config.db")
            cfgcur = cfgdb.cursor()
            
            if shipsyscursor.execute("SELECT chatid FROM list WHERE chatid = ?", (message.chat.id,)).fetchone() == None:
                bot.reply_to(message, Lang.getLoc(message.chat.id,'shipUnable'))
            else:
                if message.chat.id not in shipsyscursor.execute("SELECT chatid FROM list WHERE chatid = ?", (message.chat.id,)).fetchone():
                    bot.reply_to(message, Lang.getLoc(message.chat.id,'shipUnable')) 
                else:
                    if shipsyscursor.execute("SELECT userid, username FROM list WHERE chatid = ?", (message.chat.id,)).fetchall() == None:
                        bot.reply_to(message, Lang.getLoc(message.chat.id,'shipEmpty'))
                    elif len(shipsyscursor.execute("SELECT username FROM list WHERE chatid = ?", (message.chat.id,)).fetchall()) == 1:
                        bot.reply_to(message, Lang.getLoc(message.chat.id,'shipSingle'))
                    else:
                        userinfo = shipsyscursor.execute("SELECT username FROM list WHERE chatid = ?", (message.chat.id,)).fetchall()
                        x, y = random.sample(userinfo, k=2)
                        a = Lang.getLoc(message.chat.id,'shipAns')
                        b = a + ': ' + str(x) + ' & ' + str(y)
                        a=b.replace(',','')
                        a=a.replace('(','')
                        a=a.replace(')','')
                        a=a.replace("'", "")
                        if cfgcur.execute("SELECT ship FROM list WHERE chatid = ?", (message.chat.id,)).fetchone()[0] == None:
                            cfgcur.execute("UPDATE list SET ship = ? WHERE chatid = ?", (a, message.chat.id,))
                            bot.reply_to(message, cfgcur.execute("SELECT ship FROM list WHERE chatid = ?", (message.chat.id,)).fetchall())
                        else:
                            bot.reply_to(message, cfgcur.execute("SELECT ship FROM list WHERE chatid = ?", (message.chat.id,)).fetchall())

        except sqlite3.Error as e:
            bot.reply_to(message, e)
        finally:
            shipsysdb.commit()
            shipsysdb.close()
            cfgdb.commit()
            cfgdb.close()


@bot.message_handler(commands=['shipreset'], func=lambda message: True) # reseting ship in chat
def send_message(message):
    if system(message):
        if admin(message):
            try:
                cfgdb = sqlite3.connect("config.db")
                cfgcur = cfgdb.cursor() 

                if cfgcur.execute("SELECT ship FROM list WHERE chatid = ?", (message.chat.id,)).fetchone() == None:
                    bot.reply_to(message, Lang.getLoc(message.chat.id,'shipEmpty') + message.chat.title)
                else:
                    cfgcur.execute("UPDATE list SET ship = ? WHERE chatid = ?", (None, message.chat.id,))
                    bot.reply_to(message, Lang.getLoc(message.chat.id,'shipNull') + message.chat.title)
                    bot.send_message(-705066906, str(message.from_user.id) + " reseted ship in " + str(message.chat.id))
            except sqlite3.Error as e:
                bot.reply_to(message, e)
            finally:
                cfgdb.commit()
                cfgdb.close()


@bot.message_handler(commands=['shiplist'], func=lambda message: True) # ship's members in chat
def send_message(message):
    if system(message):
        try:
            db = sqlite3.connect("shipsys.db") 
            cursor = db.cursor()

            if cursor.execute("SELECT chatid FROM list WHERE chatid = ?", (message.chat.id,)).fetchone() is None:
                bot.reply_to(message, Lang.getLoc(message.chat.id,'shipEmpty'))
            elif cursor.execute("SELECT username FROM list WHERE chatid = ?", (message.chat.id,)) is None:
                bot.reply_to(message, Lang.getLoc(message.chat.id,'shipEmpty'))
            else:
                bot.send_message(-705066906, str(message.from_user.id) + " used command shiplist")
                a = str(cursor.execute("SELECT username FROM list WHERE chatid = ?", (message.chat.id,)).fetchall())
                a=a.replace(',','')
                a=a.replace('(','')
                a=a.replace(')','')
                a=a.replace('[','')
                a=a.replace(']','')
                a=a.replace("'", "")
                bot.reply_to(message, Lang.getLoc(message.chat.id,'shipTitle') + message.chat.title + ": " +str(a))
        except sqlite3.Error as e:
            bot.reply_to(message, e)
        finally:
            db.commit()
            db.close()


@bot.message_handler(commands=['addwelcome'], func=lambda message: True) # adding welcome to chat
def send_message(message):
    if system(message):
        if admin(message):
            a = message.text.split(' ', 1)
            try:
                cfgdb = sqlite3.connect("config.db")
                cfgcur = cfgdb.cursor() 
                noneReply = Lang.getLoc(message.chat.id,'conditionlist')
                if cfgcur.execute("SELECT welcome FROM list WHERE chatid = ?", (message.chat.id,)).fetchone() is None:
                    if len(a) == 1:
                        bot.reply_to(message, noneReply)
                    elif len(a) < 100:
                        a = a[1]
                        cfgcur.execute("INSERT INTO list (chatid, welcome) VALUES(?, ?)", (message.chat.id, a))
                        bot.reply_to(message, Lang.getLoc(message.chat.id,'welcomeSet') + message.chat.title)
                    else:
                        bot.reply_to(message, Lang.getLoc(message.chat.id,'symbolError'))
                else:
                    if len(a) == 1:
                        bot.reply_to(message, noneReply)
                    elif len(a) < 100:
                        a = a[1]
                        cfgcur.execute("UPDATE list SET welcome = ? WHERE chatid = ?", (a, message.chat.id,))
                        bot.reply_to(message, Lang.getLoc(message.chat.id,'welcomeSet') + message.chat.title)
                    else:
                        bot.reply_to(message, Lang.getLoc(message.chat.id,'symbolError'))
            except sqlite3.Error as e:
                bot.reply_to(message, e)
            finally:
                cfgdb.commit()
                cfgdb.close()


@bot.message_handler(commands=['welcometest'], func=lambda message: True) # welcome test in chat 
def send_message(message):  
    if system(message):
            try:
                cfgdb = sqlite3.connect("config.db")
                cfgcur = cfgdb.cursor() 

                if cfgcur.execute("SELECT welcome FROM list WHERE chatid = ?", (message.chat.id,)).fetchone() is None:
                    bot.reply_to(message, Lang.getLoc(message.chat.id,'welcomeError'))
                    bot.send_message(-705066906, str(message.from_user.id) + " used command welcometest in " + str(message.chat.id))
                else:
                    welcome = cfgcur.execute("SELECT welcome FROM list WHERE chatid = ?", (message.chat.id,)).fetchone()[0]
                    bot.reply_to(message, welcome)
            except sqlite3.Error as e:
                bot.reply_to(message, e)
            finally:
                cfgdb.commit()
                cfgdb.close()



@bot.message_handler(commands=['addleave'], func=lambda message: True) # add leave in chat
def send_message(message):
    if system(message):
        if admin(message):
            a = message.text.split(' ', 1)
            try:
                cfgdb = sqlite3.connect("config.db")
                cfgcur = cfgdb.cursor() 
                noneReply = Lang.getLoc(message.chat.id,'conditionlist')

                if cfgcur.execute("SELECT leave FROM list WHERE chatid = ?", (message.chat.id,)).fetchone() is None:
                    if len(a) == 1:
                        bot.reply_to(message, noneReply)
                    elif len(a) < 100:
                        a = a[1]
                        cfgcur.execute("INSERT INTO list (chatid, leave) VALUES(?, ?)", (message.chat.id, a))
                        bot.reply_to(message, Lang.getLoc(message.chat.id,'leaveSet') + message.chat.title)
                    else:
                        bot.reply_to(message, Lang.getLoc(message.chat.id,'symbolError'))
                else:
                    if len(a) == 1:
                        bot.reply_to(message, noneReply)
                    elif len(a) < 100:
                        a = a[1]
                        cfgcur.execute("UPDATE list SET leave = ? WHERE chatid = ?", (a, message.chat.id,))
                        bot.reply_to(message, Lang.getLoc(message.chat.id,'leaveSet') + message.chat.title)
                    else:
                        bot.reply_to(message, Lang.getLoc(message.chat.id,'symbolError'))
            except sqlite3.Error as e:
                bot.reply_to(message, e)
            finally:
                cfgdb.commit()
                cfgdb.close()


@bot.message_handler(commands=['leavetest'], func=lambda message: True) # leave test in chat
def send_message(message):
    if system(message):
        try:
            cfgdb = sqlite3.connect("config.db")
            cfgcur = cfgdb.cursor() 

            if cfgcur.execute("SELECT leave FROM list WHERE chatid = ?", (message.chat.id,)).fetchone() is None:
                bot.reply_to(message, Lang.getLoc(message.chat.id,'leaveError'))
            else:
                leave = cfgcur.execute("SELECT leave FROM list WHERE chatid = ?", (message.chat.id,)).fetchone()[0]
                bot.reply_to(message, leave)
        except sqlite3.Error as e:
            bot.reply_to(message, e)
        finally:
            cfgdb.commit()
            cfgdb.close()


@bot.message_handler(commands=['coin'], func=lambda message: True) # heads...... or tails?
def send_message(message):
    if system(message):
                bot.send_message(-705066906, str(message.from_user.id) + " used the command coin")
                bot.reply_to(message, Lang.getLoc(message.chat.id,'coinVar'))


@bot.message_handler(commands=['random'], func=lambda message: True) # random number
def send_message(message):
    if system(message):
        bot.send_message(-705066906, str(message.from_user.id) + " used command random")
        minPrime = 1
        maxPrime = 99999
        cached_primes = [i for i in range(minPrime, maxPrime)]
        randomId = random.choice([i for i in cached_primes])
        bot.reply_to(message, str(randomId))


@bot.message_handler(commands=['try'], func=lambda message: True) # try something 
def send_message(message):
    if system(message):
        a = message.text.split(' ')
        noneReply = Lang.getLoc(message.chat.id,'conditionlist')
        if len(a) == 1:
            bot.reply_to(message, noneReply)
        elif len(a) < 100:
            a = a[1]
            bot.reply_to(message, Lang.getLoc(message.chat.id,'tryAns'))
            bot.send_message(-705066906, str(message.from_user.id) + " used command try")
        else:
            bot.reply_to(message, Lang.getLoc(message.chat.id,'conditionlist'))


@bot.message_handler(commands=['is'], func=lambda message: True) # is something true
def send_message(message):
    if system(message):
        a = message.text.split(' ')
        noneReply = Lang.getLoc(message.chat.id,'conditionlist')
        if len(a) == 1:
            bot.reply_to(message, noneReply)
        elif len(a) < 100:
            a = a[1]
            bot.reply_to(message, Lang.getLoc(message.chat.id,'isAns'))
            bot.send_message(-705066906, str(message.from_user.id) + " used command is")
        else:
            bot.reply_to(message, Lang.getLoc(message.chat.id,'error'))


@bot.message_handler(commands=['suicide'], func=lambda message: True) # suicide variety
def send_message(message):
    if system(message):
        if message.from_user.username is not None:
            bot.reply_to(message, "@" + message.from_user.username + " " + Lang.getLoc(message.chat.id,'suicideAns'))
            bot.send_message(-705066906, str(message.from_user.id) + " used command suicide")
        else:
            bot.send_message(-705066906, str(message.from_user.id) + " used command suicide")
            bot.reply_to(message, message.from_user.first_name + " " + Lang.getLoc(message.chat.id,'suicideAns'))


@bot.message_handler(commands=['rl'], func=lambda message: True) # roulette
def send_message(message):
    if system(message):
        bot.send_message(message.chat.id, Lang.getLoc(message.chat.id,'rlPh'))
        time.sleep(1)
        if message.from_user.username is not None:
            bot.send_message(-705066906, str(message.from_user.id) + " used command roulette")
            bot.reply_to(message, "@" + message.from_user.username + Lang.getLoc(message.chat.id,'roulette'))
        else:
            bot.send_message(-705066906, str(message.from_user.id) + " used command roulette")
            bot.reply_to(message, message.from_user.first_name + Lang.getLoc(message.chat.id,'roulette'))


@bot.message_handler(commands=['rate'], func=lambda message: True) # rate something
def send_message(message):
    if system(message):
        bot.send_message(-705066906, str(message.from_user.id) + " used command rate")
        bot.reply_to(message, str(random.randrange(1,10)))


@bot.message_handler(commands=['echo'], func=lambda message: True) # echo your input
def send_message(message):
    if system(message):
        a = message.text.split(' ', 1)
        noneReply = Lang.getLoc(message.chat.id,'conditionlist')
        if len(a) == 1:
            bot.reply_to(message, noneReply)
        elif len(a) < 100:
            a = a[1]
            bot.send_message(-705066906, str(message.from_user.id) + " used command echo")
            bot.reply_to(message, a)
        else:
            bot.reply_to(message, Lang.getLoc(message.chat.id,'Error'))


@bot.message_handler(commands=['nonstop'], func=lambda message: True) # МУЗЫКА ГРОМЧЕ, ГЛАЗА ЗАКРЫТЫ
def send_message(message):
    if system(message):
        if admin(message):
            bot.send_message(message.chat.id, 'Музыка громче')
            time.sleep(2)
            bot.send_message(message.chat.id, 'Глаза закрыты')
            time.sleep(2)
            bot.send_message(message.chat.id, 'Это нонстоп')
            time.sleep(2)
            bot.send_message(message.chat.id, 'Ночью открытий')


@bot.message_handler(commands=['cid'], func=lambda message: True) # chat's id
def send_message(message):
    if message.from_user.id in adminlist:
        bot.reply_to(message, message.chat.id)
        bot.send_message(-705066906, str(message.from_user.id) + " used command cid")
    else:
        bot.send_message(-705066906, str(message.from_user.id) + " tried to use admin commands")


@bot.message_handler(commands=['stop'], func=lambda message: True) # stopping bot
def send_message(message):
    if message.from_user.id in adminlist:
        bot.reply_to(message, ":(")
        bot.stop_polling()
        print('Bot stopped')
    else:
        bot.send_message(-705066906, str(message.from_user.id) + " tried to use admin commands")


@bot.message_handler(commands=['info'], func=lambda message: True) # (user name, id, username, chat id)
def send_message(message):
    if message.from_user.id in adminlist:
        if message.reply_to_message is None:
            bot.reply_to(message, "Message is not selected")
        elif message.reply_to_message.from_user.username is None:
            bot.reply_to(message, "User: " + str(message.reply_to_message.from_user.first_name + "\nID: " + str(message.reply_to_message.from_user.id)
            + "\nChat ID: " + str(message.reply_to_message.chat.id)))
        else:
            bot.reply_to(message, "User: " + str(message.reply_to_message.from_user.first_name + "\nUsername: @" + str(message.reply_to_message.from_user.username) +  "\nId: " + str(message.reply_to_message.from_user.id)
            + "\nChat ID: " + str(message.reply_to_message.chat.id)))


@bot.message_handler(commands=['addtbl'], func=lambda message: True) # add to ban list
def send_message(message):
    if message.from_user.id in adminlist:
        a = message.text.split(' ')
        noneReply = Lang.getLoc(message.chat.id,'conditionlist')
        try:
            cfgdb = sqlite3.connect("config.db")
            cfgcur = cfgdb.cursor() 

            
            if len(a) == 1:
                bot.reply_to(message, noneReply)
            elif len(a) < 100:
                a = a[1]
                if cfgcur.execute("SELECT banlist FROM list WHERE banlist = ?", (a,)).fetchone() is not None:
                    bot.reply_to(message, "id" + str(a) + " уже в банлисте")
                else:
                    cfgcur.execute("INSERT INTO list (banlist) VALUES(?)", (a,))
                    bot.reply_to(message, "id" + a + " был добавлен в банлист")
            else:
                bot.reply_to(message, "Сообщение должно содержать не более 100 символов")
        except sqlite3.Error as e:
            bot.reply_to(message, e)
        finally:
            cfgdb.commit()
            cfgdb.close()
        
    else:
        bot.send_message(-705066906, str(message.from_user.id) + " tried to use admin commands")


@bot.message_handler(commands=['rmfbl'], func=lambda message: True) # remove from ban list 
def send_message(message):
    if message.from_user.id in adminlist:
        b = message.text.split(' ')
        noneReply = random.choice(ru.conditionlist)
        try:
            cfgdb = sqlite3.connect("config.db")
            cfgcur = cfgdb.cursor() 

            a = str(cfgcur.execute("SELECT banlist FROM list WHERE banlist = banlist").fetchall())
            a=a.replace(',','')
            a=a.replace('(','')
            a=a.replace(')','')
            a=a.replace('[','')
            a=a.replace(']','')
            a=a.replace("'", "")

            if len(b) == 1:
                bot.reply_to(message, noneReply)
            else:
                b = b[1]
                if b in a:
                    cfgcur.execute("DELETE FROM list WHERE banlist = ?", (b,))
                    bot.reply_to(message, b + " был удален из банлиста")
                    bot.send_message(-705066906, b + " is deleted from the banlist")
                else:
                    bot.reply_to(message, b + " не был найден в банлисте")
        except sqlite3.Error as e:
            bot.reply_to(message, e)
        finally:
            cfgdb.commit()
            cfgdb.close()
        
    else:
        bot.send_message(-705066906, str(message.from_user.id) + " tried to use admin commands")


@bot.message_handler(commands=['banlist'], func=lambda message: True) # ban list
def send_message(message):
    if message.from_user.id in adminlist:
        try:
            cfgdb = sqlite3.connect("config.db")
            cfgcur = cfgdb.cursor() 

            if cfgcur.execute("SELECT banlist FROM list").fetchone() is None:
                bot.reply_to(message, Lang.getLoc(message.chat.id,'leaveError'))
            else:
                leave = cfgcur.execute("SELECT banlist FROM list").fetchall()
                bot.reply_to(message, leave)
        except sqlite3.Error as e:
            bot.reply_to(message, e)
        finally:
            cfgdb.commit()
            cfgdb.close()
    else:
        bot.send_message(-705066906, str(message.from_user.id) + " tried to use admin commands")


@bot.message_handler(commands=['report'], func=lambda message: True) # report about something to admin
def send_message(message):
    try:
        cfgdb = sqlite3.connect("config.db")
        cfgcur = cfgdb.cursor() 

        if message.from_user.id in cfgcur.execute("SELECT banlist FROM list").fetchall():
            bot.send_message(-705066906, str(message.from_user.id) + " is banned")
        else:
            reportMess = message.text
            regex = '(/report|@OscarSinclair_bot)'
            reportRed = re.sub(regex, '', reportMess)
            noneReply = random.choice(ru.conditionlist)
            if reportRed == "":
                bot.reply_to(message, noneReply)
            elif len(reportRed) < 20:
                bot.reply_to(message, "Репорт был отправлен")
                bot.send_message(-705066906, str(message.from_user.id) + " said" + reportRed)
            else:
                bot.reply_to(message, "Сообщение должно содержать не более 20 символов")
    except sqlite3.Error as e:
        bot.reply_to(message, e)
    finally:
        cfgdb.commit()
        cfgdb.close()
    


@bot.message_handler(content_types="new_chat_members", func=lambda message: True)
def send_message(message):
    if system(message):
        bot.send_message(-705066906, str(message.from_user.id) + " just joined " + str(message.chat.id))
        try:
            cfgdb = sqlite3.connect("config.db")
            cfgcur = cfgdb.cursor() 

            if cfgcur.execute("SELECT welcome FROM list WHERE chatid = ?", (message.chat.id,)).fetchone() is None:
                bot.reply_to(message, Lang.getLoc(message.chat.id,'welcomeError'))
            else:
                welcome = cfgcur.execute("SELECT welcome FROM list WHERE chatid = ?", (message.chat.id,)).fetchone()[0]
                bot.reply_to(message, welcome)
        except sqlite3.Error as e:
            bot.reply_to(message, e)
        finally:
            cfgdb.commit()
            cfgdb.close()

@bot.message_handler(content_types="left_chat_member", func=lambda message: True)
def send_message(message):
    if system(message):
        bot.send_message(-705066906, str(message.from_user.id) + " just left " + str(message.chat.id))
        try:
            cfgdb = sqlite3.connect("config.db")
            cfgcur = cfgdb.cursor() 

            if cfgcur.execute("SELECT leave FROM list WHERE chatid = ?", (message.chat.id,)).fetchone() is None:
                pass
            else:
                leave = cfgcur.execute("SELECT leave FROM list WHERE chatid = ?", (message.chat.id,)).fetchone()[0]
                bot.reply_to(message, leave)
        except sqlite3.Error as e:
            bot.reply_to(message, e)
        finally:
            cfgdb.commit()
            cfgdb.close()


bot.infinity_polling()
