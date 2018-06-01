# - *- coding: utf- 8 - *-
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, CallbackQueryHandler)
import logging
import json

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

#LIST_OF_ADMINS = [123456]
LIST_OF_ADMINS = []

def start(bot, update):
    bot.send_message(update.message.chat_id, "Ciao a tutti, al momento mi occupo solo degli inviti a cena."+
    "Quando Vale o Cazza creano un invito a cena potete rispondere con il comando /inv. "+
    "Cliccate uno degli inviti attivi per confermare o annullare la preseza."+
    "Digitate /invitati per vedere la lista dei presenti")

def cena(bot, update, args=None):
    user_id = update.effective_user.id
    if isAdmin(user_id):
        realCena(bot, update, args)
    else:
        bot.send_message(update.message.chat_id, "Comando non disponibile per {}.".format(user_id))
        return
    
def realCena(bot, update, args=None):
    if not args:
        bot.send_message(update.message.chat_id, "Quale cena?")
    else:
        data = openJdata()
        exist = False
        if not data['inviti']:
            exist = False
        else:    
            for p in data['inviti']:
                if p['nome']==args[0]:
                    exist = True
        
        if exist:
            bot.send_message(update.message.chat_id, "Nome duplicato, scegli un altro nome.")
        elif len(data['inviti'])>5:
            bot.send_message(update.message.chat_id, "Hai raggiunto il numero massimo di inviti.")
        else:
            data['inviti'].append({  
                'nome': args[0],
                'presenti': [],
                })
            writeJdata(data)
            bot.send_message(update.message.chat_id, "Chi viene a cena "+args[0]+"?")
        
def inv(bot, update):
    user_name = update.effective_user.first_name
    data = openJdata()
    keyboard = []
    if not data['inviti']:
        bot.send_message(update.message.chat_id, "Nessun invito attivo.")
    else:
        for p in data['inviti']:
            extTxt = ''
            add = 'add'
            if user_name in p['presenti']:
                extTxt = ' (esci)'
                add = 'del'
            keyboard = keyboard + [[InlineKeyboardButton(p['nome']+extTxt, callback_data=p['nome']+'||'+add)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Vuoi unirti a?:', reply_markup=reply_markup)
        
def button(bot, update):
    user_name = update.effective_user.first_name
    user_id = update.effective_user.first_name
    query = update.callback_query
    res = format(query.data)
    res = res.split("||")
    data = openJdata()
    
    #logger.warning(res[0] + '--'+res[1])
    if res[1] == 'add':
        for p in data['inviti']:
            if p['nome']==res[0]:
                p['presenti'].append(user_name)
                writeJdata(data)
                bot.edit_message_text(format(user_id)+" iscritto da "+res[0]+"", query.message.chat_id, query.message.message_id)
    else:
        for p in data['inviti']:
            if p['nome']==res[0]:    
                p['presenti'].remove(user_name)
                writeJdata(data)
                bot.edit_message_text(format(user_id)+" rimosso da "+res[0]+"", query.message.chat_id, query.message.message_id)
    
def invitati(bot, update):
    output = ''
    data = openJdata()
    logger.warning(data, update, error)
    if not data['inviti']:
        bot.send_message(update.message.chat_id, "Nessun invito attivo.")
    else:
        for p in data['inviti']:
            output = output +'<b>'+ p['nome']+'</b>:\n'
            for pr in p['presenti']:
                output = output + pr +':\n'
        bot.send_message(update.message.chat_id, output, ParseMode.HTML)
    
    
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def reset(bot, update):
    user_id = update.effective_user.id
    if isAdmin(user_id):
        with open('data.txt', 'w') as outfile:  
            json.dump({"inviti": []}, outfile)
        bot.send_message(update.message.chat_id, "Inviti azzerati.")
    else:
        bot.send_message(update.message.chat_id, "Comando non disponibile per {}.".format(user_id))

def isAdmin(idCurrUser):
    if idCurrUser not in LIST_OF_ADMINS:
        return False
    else:
        return True

def openJdata():
    with open('data.txt') as json_file:
        tempj = json.load(json_file)
    return tempj
    
def writeJdata(data):
    with open('data.txt', 'w') as outfile:  
        json.dump(data, outfile)
        
def photohand(bot, update):
    bot.send_message(update.message.chat_id, "Foto inviata")

def main():
    # Create Updater object and attach dispatcher to it
    updater = Updater('KEY')
    dp = updater.dispatcher
    # Add command handler to dispatcher
    start_handler = CommandHandler('start',start)
    dp.add_handler(start_handler)

    cena_handler = CommandHandler('cena', cena, pass_args=True)
    dp.add_handler(cena_handler)

    invitati_handler = CommandHandler('invitati', invitati)
    dp.add_handler(invitati_handler)

    reset_handler = CommandHandler('reset', reset)
    dp.add_handler(reset_handler)

    inv_handler = CommandHandler('inv', inv)
    dp.add_handler(inv_handler)

    photo_handler = MessageHandler(Filters.photo, photohand)
    dp.add_handler(photo_handler)

    dp.add_handler(CallbackQueryHandler(button))
    # log all errors
    dp.add_error_handler(error)
    # Start the bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C
    updater.idle()
    
'''
if user_name in LISTA_ISCRITTI or user_name in LISTA_NON_ISCRITTI:
    bot.send_message(update.message.chat_id, format(user_name)+" hai già risposto.")
else:
    keyboard = [[InlineKeyboardButton("Sì", callback_data='y'),
                 InlineKeyboardButton("No", callback_data='n')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Ci sei?:', reply_markup=reply_markup)
'''    

if __name__ == '__main__':
    main()