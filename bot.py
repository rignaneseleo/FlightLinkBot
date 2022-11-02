#!/usr/bin/python
import telebot
from telebot import types
from config import TOKEN
import time
import script

# setup dataset and bot
dataset = script.DataSet()
bot = telebot.TeleBot(TOKEN)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, this bot helps you get a link of your flight, so that your mom doesn't get worried!
""")


# Handle all other messages
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, """This bot can be used only in the chat.
Use @FlightLinkBot in the chat to get a link of your flight.
    
Examples:
@FlightLinkBot Milan Madrid
@FlightLinkBot BGY - Madrid
@FlightLinkBot BGY MDR""")


# Handle inline texts
@bot.inline_handler(lambda query: len(query.query) > 3)
def text_callback(query):
    message = "✈️ Follow my {} flight from {} to {}:\r\n\r\n{}"
    if query.from_user.language_code == 'it':
        message = "✈️ Segui il mio volo {} da {} a {}:\r\n\r\n{}"
    text = query.query
    routes = script.find_route(text)
    results = []

    for route in routes:
        r = types.InlineQueryResultArticle(
            # The id of our inline result
            thumb_url=route.getIconUrl(),
            id=routes.index(route),
            title="[%s] %s (%s) - %s (%s)" % (route.code_IATA,
                                              route.departure_airport.city, route.departure_airport.code_iata,
                                              route.arrival_airport.city, route.arrival_airport.code_iata),
            input_message_content=types.InputTextMessageContent(message
                                                                .format(route.airline.name, route.departure_airport.city, route.arrival_airport.city, route.getFlightAwareLink())
                                                                )
        )
        results.append(r)
    print("Sending results to query " + query.query)
    # show the choices
    bot.answer_inline_query(query.id, results)


# main
while True:
    try:
        bot.polling(True)
    except Exception as e:
        print(e)
        time.sleep(5)
