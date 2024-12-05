import logging
import os
import sys
from typing import List
import script
from script import DataSet

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    InlineQueryHandler,
    ContextTypes,
)
from telegram.error import TelegramError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("Missing required BOT_TOKEN environment variable")
    sys.exit(1)

# Load dataset once at startup
try:
    dataset = DataSet()
    logger.info("Dataset loaded successfully")
except Exception as e:
    logger.error(f"Failed to load dataset: {e}")
    sys.exit(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    try:
        await update.effective_message.reply_text(
            """Hi there, this bot helps you get a link of your flight, so that your mom can track it and doesn't get worried 😌
            
Type @FlightLinkBot in any chat to instantly get a link of your flight.
        
Examples:
@FlightLinkBot Milan Madrid
@FlightLinkBot BGY - Madrid
@FlightLinkBot BGY MDR

Code: https://github.com/rignaneseleo/FlightLinkBot
Credits: @rignaneseleo ✌🏻"""
        )
        await update.effective_message.reply_video(
            "https://raw.githubusercontent.com/rignaneseleo/FlightLinkBot/main/res/example.mp4"
        )
        logger.info(f"Start command used by user {update.effective_user.id}")
    except TelegramError as e:
        logger.error(f"Error sending start message: {e}")


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all other messages"""
    try:
        await update.effective_message.reply_text(
            """Type @FlightLinkBot in any chat to instantly get a link of your flight.
        
Examples:
@FlightLinkBot Milan Madrid
@FlightLinkBot BGY - Madrid
@FlightLinkBot BGY MDR

Code: https://github.com/rignaneseleo/FlightLinkBot
Credits: @rignaneseleo ✌🏻"""
        )
        logger.info(f"Reply sent to user {update.effective_user.id}")
    except TelegramError as e:
        logger.error(f"Error sending reply: {e}")


def get_flight_results(query: str) -> List[InlineQueryResultArticle]:
    """Get flight search results"""
    try:
        routes = script.find_route(query)
        results = []

        for i, route in enumerate(routes[0:50]):
            results.append(
                InlineQueryResultArticle(
                    id=i,
                    thumb_url=route.getIconUrl(),
                    title=f"[{route.code_IATA}] {route.departure_airport.city} ({route.departure_airport.code_iata}) - {route.arrival_airport.city} ({route.arrival_airport.code_iata})",
                    input_message_content=InputTextMessageContent(
                        f"✈️ Follow this {route.airline.name} flight from {route.departure_airport.city} to {route.arrival_airport.city}:\n\n{route.getFlightAwareLink()}"
                    ),
                    url=route.getFlightAwareLink(),
                )
            )

        if not results:
            results.append(
                InlineQueryResultArticle(
                    id=0,
                    thumb_url="https://raw.githubusercontent.com/rignaneseleo/FlightLinkBot/main/res/error.png",
                    title="No flights found, try with a different query",
                    input_message_content=InputTextMessageContent(query),
                )
            )

        return results
    except Exception as e:
        logger.error(f"Error getting flight results: {e}")
        return []


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries"""
    try:
        query = update.inline_query.query
        results = get_flight_results(query)
        await update.inline_query.answer(results)
        logger.info(f"Inline query '{query}' returned {len(results)} results")
    except TelegramError as e:
        logger.error(f"Error handling inline query: {e}")


def main() -> None:
    """Start the bot"""
    try:
        # Set up the application and pass it your bot's token
        application = Application.builder().token(BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
        application.add_handler(InlineQueryHandler(inline_query, pattern="^.{3,}$"))

        # Start the Bot
        application.run_polling()

    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
