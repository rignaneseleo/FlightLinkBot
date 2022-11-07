import logging
import os
import script
from script import DataSet

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler


def start(update, context):
    update.effective_message.reply_text(
        "Hi there, this bot helps you get a link of your flight, so that your mom can track it and doesn't get worried!")

# Handle all other messages
def reply(update, context):
    update.effective_message.reply_text("""Use @FlightLinkBot in any chat to instanly get a link of your flight so your mom can track it and doesn't get worried.
    
Examples:
@FlightLinkBot Milan Madrid
@FlightLinkBot BGY - Madrid
@FlightLinkBot BGY MDR

Credits: @rignaneseleo ✌🏻""")


# Handle inline texts
def inline_query(update, context):
    message = "✈️ Follow my {} flight from {} to {}:\r\n\r\n{}"
    #if query.from_user.language_code == 'it':
    #    message = "✈️ Segui il mio volo {} da {} a {}:\r\n\r\n{}"
    text = update.inline_query.query
    routes = script.find_route(text)
    results = []

    for route in routes:
        r = InlineQueryResultArticle(
            # The id of our inline result
            thumb_url=route.getIconUrl(),
            id=routes.index(route),
            title="[%s] %s (%s) - %s (%s)" % (route.code_IATA,
                                              route.departure_airport.city, route.departure_airport.code_iata,
                                              route.arrival_airport.city, route.arrival_airport.code_iata),
            input_message_content=InputTextMessageContent(message
                                                                .format(route.airline.name, route.departure_airport.city, route.arrival_airport.city, route.getFlightAwareLink())
                                                                )
        )
        results.append(r)
    print("Sending results to query: " + text)
    # show the choices
    update.inline_query.answer(results)


if __name__ == "__main__":
    # heroku app name
    NAME = "flight-link-bot"
    # get TOKEN from Heroku Config Vars
    TOKEN = os.environ['TOKEN']

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    #load the dataset to search a flight
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
    dp.add_handler(InlineQueryHandler(inline_query))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url=f"https://{NAME}.herokuapp.com/{TOKEN}")
    updater.idle()
