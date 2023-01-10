import time
import math
import telegram.ext
from moralis import evm_api
from frozendict import frozendict
import datetime
from sqlitedict import SqliteDict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from selenium import webdriver
import os
import requests
from flask import Flask, request



db = SqliteDict('./db.sqlite', autocommit=True)

# take a snapshot of the chart
# splinter: https://splinter.readthedocs.io/en/latest/install/driver_install.html

app = Flask(__name__)
TOKEN = "5848336987:AAGeAmMwEkS7i4Y_QbSTbSnNNF1rYfRnJWI"
api_key = "yUPc8FIAEhUe4S9IfGYV0w3XgpxmizxvFDU0bC9zvcnQ0OAUNxMavTh0rhTvLcMH"
ADDRESS = "0xEcdF61B4d2a4f84bAB59f9756ccF989C38bf99F5"

LAST_SCRAPE = datetime.datetime.now()

def get():
    print()
    params = {
        "address": ADDRESS,
        "function_name": "calculatePrice",
        "chain": "bsc",
    }

    params2 = {
        "address": ADDRESS,
        "function_name": "totalSupply",
        "chain": "bsc",
    }
    abi = {
            "inputs": [],
            "name": "calculatePrice",
            "outputs": [
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        }

    abi = {
        "inputs": [],
        "name": "calculatePrice",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
    abi2 = {
            "inputs": [],
            "name": "totalSupply",
            "outputs": [
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        }
    body = {
        "abi": [frozendict(abi)],
        "params": {},
    }

    body2 = {
        "abi": [frozendict(abi2)],
        "params": {},
    }

    price = evm_api.utils.run_contract_function(
        api_key=api_key,
        params=params,
        body=body,
    )
    total_supply = evm_api.utils.run_contract_function(
        api_key=api_key,
        params=params2,
        body=body2,
    )

    return (price, total_supply)

def get_lp():
    balance_params = {
        "address": ADDRESS,
        "chain": "bsc",
    }

    value = evm_api.token.get_wallet_token_balances(api_key=api_key, params=balance_params)
    return int(value[0]['balance']) / 1000000000000000000


#https://www.youtube.com/watch?v=LN1a0JoKlX8&ab_channel=RajsuthanOfficial
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
    (wei_price, ) = get()
    price_var = int(wei_price) / 1000000000000000000
    db['price'] = price_var
    db['last_time'] = datetime.datetime.now()

def price(update, context):
    last_time = db['last_time'] + datetime.timedelta(minutes=3)
    last_image_fetch = db['last_time'] + datetime.timedelta(minutes=0)
    price_var = 0
    total_supply_val = 0
    print(last_time)
    print(datetime.datetime.now())
    if last_image_fetch < datetime.datetime.now():
        try:
            fetch_image()
        except:
            print(Exception)
    image = open('image.png', 'rb')
    if last_time < datetime.datetime.now():
        print('refetched')
        (wei_price, total_supply) = get()
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

    keyboard = [
        [InlineKeyboardButton("Buy",  url='https://2spice.link/swap', callback_data='https://2spice.link/swap')],
        [InlineKeyboardButton("Chart", url='https://2spice.link/chart', callback_data='https://2spice.link/chart')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = f"Token: 2Spice(Spice)\nPrice: ${round(price_var, 2)}\nTotal Supply: {round(total_supply_val, 2)}\n "\
                   f"MarketCap: ${round((price_var*total_supply_val), 0)}\n" \
                   f"LP holdings: {round(backing_lp)} BUSD (${round(backing_lp)})"
    update.message.reply_photo(image, caption=message_text, reply_markup=reply_markup)
    # update.message.reply_text(message_text, reply_markup=reply_markup)



def content(update, context):
    update.message.reply_text("chart link: https://2spice.link/chart")


def contact(update, context):
    price = 0
    total_supply = 0
    update.message.reply_text(f"price: {price}\n total supply {total_supply}\n")


def handleMessage(update, context):
    update.message.reply_text(f"You said {update.message.text}")



updater = telegram.ext.Updater(token=TOKEN, use_context=True)
disp = updater.dispatcher

def main():
    disp.add_handler(telegram.ext.CommandHandler("start", start))
    disp.add_handler(telegram.ext.CommandHandler("help", help))
    disp.add_handler(telegram.ext.CommandHandler("price", price))
    disp.add_handler(telegram.ext.CommandHandler("contact", contact))
    disp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, handleMessage))

    updater.start_polling()
    updater.idle()

@app.route('/', methods=['POST'])
def home():
    main()



@app.route('/sethook', methods=['POST', 'GET'])
def sethook():
    updater.start_webhook(f'http://127.0.0.1:5000/{TOKEN}')
    return 'success'

if __name__ == '__main__':
    main()
    app.run(debug=True)