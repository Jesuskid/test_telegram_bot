import telegram.ext

TOKEN = "5848336987:AAGeAmMwEkS7i4Y_QbSTbSnNNF1rYfRnJWI"


def start(update, context):
    update.message.reply_text("Hello welcome to neural bot")


def help(update, context):
    update.message.reply_text("""
    The following commands are available
    /start
    /price
    /content
    /contact
    """)


def price(udpate, context):
    # get snapshot of the chat
    # get latest price
    # total supply
    # Busd backing
    # price
    ticker = context.args[0]
    pass


image = open('image.png', 'rb')

print(image)
def content(update, context):
    update.message.reply_text("chart link: https://2spice.link/chart")


def contact(update, context):
    price = 0
    total_supply = 0
    update.message.reply_photo(image)
    update.message.reply_text(f"price: {price}\n total supply {total_supply}\n")


def handleMessage(update, context):
    update.message.reply_text(f"You said {update.message.text}")


updater = telegram.ext.Updater(token=TOKEN, use_context=True)
disp = updater.dispatcher

disp.add_handler(telegram.ext.CommandHandler("start", start))
disp.add_handler(telegram.ext.CommandHandler("help", help))
disp.add_handler(telegram.ext.CommandHandler("content", content))
disp.add_handler(telegram.ext.CommandHandler("contact", contact))
disp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, handleMessage))
updater.start_polling()
updater.idle()
