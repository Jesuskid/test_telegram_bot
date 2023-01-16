import time
from moralis import evm_api
import datetime
from sqlitedict import SqliteDict
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from selenium import webdriver
from flask import Flask, request
import os
import pymongo

MONGO_HOST = "167.99.183.64"
MONGO_PORT = 56728
con = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)

PORT = int(os.environ.get('PORT', '5000'))

URL = os.environ.get('URL')

db = SqliteDict('./db.sqlite', autocommit=True)

TOKEN = os.environ.get("TOKEN")
api_key = os.environ.get('MORALIS_API')
ADDRESS = "0xEcdF61B4d2a4f84bAB59f9756ccF989C38bf99F5"

LAST_SCRAPE = datetime.datetime.now()
WEI = 1000000000000000000



def get_price():
    user_table = con['parse']['NewPrice']
    tab = user_table.find().sort('block_timestamp', -1).limit(1)
    price = 0
    totalSupply = 0
    for x in tab:
        print(x)
        price = int(x['currentPrice']) / WEI
        totalSupply = int(x['totalSupply']) / WEI

    return (price, totalSupply)


def get_lp():
    balance_params = {
        "address": ADDRESS,
        "chain": "bsc",
    }

    value = evm_api.token.get_wallet_token_balances(api_key=api_key, params=balance_params)
    return int(value[0]['balance']) / 1000000000000000000


# https://www.youtube.com/watch?v=LN1a0JoKlX8&ab_channel=RajsuthanOfficial
def fetch_image():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54"

    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
    driver.get('https://2spice.link/chart')
    time.sleep(5)
    btn = driver.find_element_by_xpath('/html/body/div/div/div/div/div/div[1]/div/div[1]/button[1]')
    btn.click()
    time.sleep(5)
    element = driver.find_element_by_css_selector('canvas')
    driver.get_screenshot_as_file('image.png')
    print('done')


def start(update, context):
    update.message.reply_text("Hello welcome to 2spice telegram bot")


def help(update, context):
    update.message.reply_text("""
    The following commands are available
    /start - 
    /price -
    /content -
    /contact -
    """)


def set_price_var():
    (wei_price, total_ss) = get_price()
    price_var = wei_price
    db['price'] = price_var
    db['last_time'] = datetime.datetime.now()
    db['total_supply'] = total_ss
    backing_lp = get_lp()
    db['lp'] = backing_lp


set_price_var()


def price():
    last_time = db['last_time'] + datetime.timedelta(minutes=3)
    last_image_fetch = db['last_time'] + datetime.timedelta(minutes=30)
    price_var = 0
    total_supply_val = 0
    print(last_time)
    # print(datetime.datetime.now())
    # if last_image_fetch < datetime.datetime.now():
    #     try:
    #         fetch_image()
    #     except:
    #         print(Exception)
    if last_time < datetime.datetime.now():
        print('refetched')
        (wei_price, total_supply) = get_price()
        price_var = int(wei_price) / 1000000000000000000
        total_supply_val = int(total_supply) / 1000000000000000000
        backing_lp = get_lp()
        db['price'] = price_var
        db['last_time'] = datetime.datetime.now()
        db['total_supply'] = total_supply_val
        db['lp'] = backing_lp
    else:
        print('not')
        price_var = db['price']
        total_supply_val = db['total_supply']
        backing_lp = db['lp']

    # keyboard = [
    #     [InlineKeyboardButton("Buy",  url='https://2spice.link/swap', callback_data='https://2spice.link/swap')],
    #     [InlineKeyboardButton("Chart", url='https://2spice.link/chart', callback_data='https://2spice.link/chart')]
    # ]
    #
    # reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = f"Token: 2Spice(Spice)\nPrice: ${round(price_var, 4)}\nTotal Supply: {round(total_supply_val, 2)}\n " \
                   f"MarketCap: ${round((price_var * total_supply_val), 0)}\n" \
                   f"LP holdings: {round(backing_lp)} BUSD (${round(backing_lp)})"

    return message_text


app = Flask(__name__)
# from teleflask import Teleflask
# from teleflask.messages import Message


bot = telegram.Bot(token=TOKEN)


@app.route('/', methods=["GET", 'POST'])
def index():
    # updater = telegram.ext.Updater(token=TOKEN, use_context=True)
    if request.method == 'POST':
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.effective_chat.id
        text = update.message.text
        if (text == 'price'):
            bot.sendMessage(text=f'You said {text}', chat_id=chat_id)
        elif (text == 'contact'):
            pass
    else:
        bot.sendMessage(text='Hi Logoa', chat_id=-769764926)
    return '.'


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    print('received command')
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    text = update.message.text
    if (text.strip() == '/price'):
        print(text)
        (wei_price, total_ss) = get_price()
        keyboard = [
            [InlineKeyboardButton("Buy", url='https://2spice.link/swap', callback_data='https://2spice.link/swap')],
            [InlineKeyboardButton("Chart", url='https://2spice.link/chart', callback_data='https://2spice.link/chart')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f"Token: 2Spice(Spice)\nPrice: ${round(wei_price, 3)}\nTotal Supply: {round(total_ss, 2)}\n " \
                   f"MarketCap: ${round((wei_price * total_ss), 2)}\n"\
                   f"LP holdings: {round((wei_price * total_ss), 2)} BUSD (${round((wei_price * total_ss) * 1.0001)})"
        image = open('image.png', 'rb')
        bot.sendPhoto(chat_id=chat_id, caption=message, photo=image, reply_markup=reply_markup)
        image.close()
    else:
        bot.sendMessage(chat_id=chat_id, text='message')
    return 'ok'


@app.route('/setWebHook/<string:url>')
def setHook(url):
    bot = telegram.Bot(token=TOKEN)
    Url = URL if URL else url
    hook = "{URL}{TOKEN}".format(URL=Url, TOKEN=TOKEN)
    print('HOOK URL -----' + " " + hook)
    s = bot.setWebhook()
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


if __name__ == '__main__':
    app.run(threaded=True)
