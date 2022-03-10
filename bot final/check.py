from cfg import *
import sqlite3


def system(message): # checking is user's id in banlist else true
    try:
        cfgdb = sqlite3.connect("config.db")
        cfgcur = cfgdb.cursor() 
        a = str(cfgcur.execute("SELECT banlist FROM list").fetchall())
        a=a.replace(',,',',')
        a=a.replace('(','')
        a=a.replace(')','')
        a=a.replace('[','')
        a=a.replace(']','')
        a=a.replace("'", "")
        if str(message.from_user.id) not in a:
            return True
        else:
            bot.send_message(-705066906, str(message.from_user.id) + ' is banned')
    except sqlite3.Error as e:
            bot.reply_to(message, e)
    finally:
            cfgdb.commit()
            cfgdb.close()
        

def admin(message):  # checking is user an admin
    if bot.get_chat_member(message.chat.id, message.from_user.id).status in ["administrator", "creator"] or message.from_user.id in adminlist:
        return True
    else:
        bot.reply_to(message, str(message.from_user.id) + ' not an admin')
