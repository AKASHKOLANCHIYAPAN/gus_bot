from telegram.ext import Updater, MessageHandler, Filters

TOKEN ="8176327658:AAFCoam7gP-AOun057WCZY8b84QTEo7l44c" 


def echo(update, context):
    update.message.reply_text("Gus is online.")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

updater.start_polling()
print("Bot is running...")
updater.idle()
