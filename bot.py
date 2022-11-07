import logging
import os
import script
from script import DataSet

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler


def start(update, context):
    update.effective_message.reply_text(
        """Hi there, this bot helps you get a link of your flight, so that your mom can track it and doesn't get worried 😌
        
Type @FlightLinkBot in any chat to instanly get a link of your flight.
    
Examples:
@FlightLinkBot Milan Madrid
@FlightLinkBot BGY - Madrid
@FlightLinkBot BGY MDR

Code: https://github.com/rignaneseleo/FlightLinkBot
Credits: @rignaneseleo ✌🏻"""
        )
    update.effective_message.reply_video("https://raw.githubusercontent.com/rignaneseleo/FlightLinkBot/main/res/example.mp4")

# Handle all other messages


def reply(update, context):
    update.effective_message.reply_text("""Type @FlightLinkBot in any chat to instanly get a link of your flight.
    
Examples:
@FlightLinkBot Milan Madrid
@FlightLinkBot BGY - Madrid
@FlightLinkBot BGY MDR

Code: https://github.com/rignaneseleo/FlightLinkBot
Credits: @rignaneseleo ✌🏻""")





# Handle inline texts
def inline_query(update, context):
    message = "✈️ Follow this {} flight from {} to {}:\r\n\r\n{}"
    # if query.from_user.language_code == 'it':
    #    message = "✈️ Segui il mio volo {} da {} a {}:\r\n\r\n{}"
    text = update.inline_query.query
    routes = script.find_route(text)
    results = []

    for route in routes[0:50]:
        r = InlineQueryResultArticle(
            # The id of our inline result
            thumb_url=route.getIconUrl(),
            id=routes.index(route),
            title="[%s] %s (%s) - %s (%s)" % (route.code_IATA,
                                              route.departure_airport.city, route.departure_airport.code_iata,
                                              route.arrival_airport.city, route.arrival_airport.code_iata),
            input_message_content=InputTextMessageContent(message
                                                          .format(route.airline.name, route.departure_airport.city, route.arrival_airport.city, route.getFlightAwareLink())
                                                          ),
            url=route.getFlightAwareLink(),

        )
        results.append(r)
    print("Found "+str(len(results))+" results to query: " + text)

    if len(results) == 0:
        results.append(InlineQueryResultArticle(
            thumb_url="https://raw.githubusercontent.com/rignaneseleo/FlightLinkBot/main/res/error.png"
            id=0,
            title="No flights found, try with a different query",
            input_message_content=InputTextMessageContent("-")
        ))

    # show the choices
    update.inline_query.answer(results)


if __name__ == "__main__":
    # heroku app name
    NAME = "flight-link-bot"
    # get TOKEN from Heroku Config Vars
    TOKEN = os.environ['TOKEN']

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # load the dataset to search a flight
    dataset = DataSet()

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Add handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, reply))
    dp.add_handler(InlineQueryHandler(inline_query, pattern="^.{3,}$"))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url=f"https://{NAME}.herokuapp.com/{TOKEN}")
    updater.idle()
