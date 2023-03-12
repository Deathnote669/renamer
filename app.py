import logging
import os
import time

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(name)


# Define the start command
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Send me a file and I will rename it for you.')


# Define the rename command
def rename(update: Update, context: CallbackContext) -> None:
    """Rename the file sent by the user."""
    # Get the file sent by the user
    file = update.message.document or update.message.photo or update.message.video
    if not file:
        update.message.reply_text('Please send a supported file type (document, photo, or video).')
        return
    
    # Get the new name from the message sent by the user
    new_name = update.message.text.strip()[7:]
    if not new_name:
        update.message.reply_text('Please enter a new name for the file after the command /rename.')
        return
    
    # Download the file to the local filesystem
    file_path = context.bot.get_file(file.file_id).file_path
    file_name = file.file_name
    download_path = f'{time.time()}_{file_name}'
    context.bot.download_file(file_path, download_path)
    
    # Rename the file
    new_path = os.path.join(os.path.dirname(download_path), new_name)
    os.rename(download_path, new_path)
    
    # Upload the renamed file to Telegram
    context.bot.send_document(chat_id=update.message.chat_id, document=open(new_path, 'rb'))
    
    # Delete the local file
    os.remove(new_path)


# Define the cancel command
def cancel(update: Update, context: CallbackContext) -> None:
    """Cancel the current operation."""
    update.message.reply_text('Operation cancelled.', reply_markup=ForceReply(selective=True))
    

# Define the error handler
def error(update: Update, context: CallbackContext) -> None:
    """Log the error and send a message to the user."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text('Sorry, something went wrong. Please try again.')


def main() -> None:
    """Start the bot."""
    # Set up the updater
    updater = Updater(os.environ.get('BOT_TOKEN'))
    dispatcher = updater.dispatcher
    
    # Set up the handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('rename', rename))
    dispatcher.add_handler(CommandHandler('cancel', cancel))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, cancel))
    dispatcher.add_error_handler(error)
    
    # Start the bot
    updater.start_polling()
    updater.idle()


if name == 'main':
    main()
