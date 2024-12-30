import logging
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
import requests
from datetime import datetime

# Flask setup
app = Flask(__name__)

# Telegram Bot Token
TOKEN = '7772489059:AAFOWyMsWPVy78lwLd7mOxoiCA-CXtJNX7M'

# API Endpoint and Headers
API_URL = 'https://ebantisaiapi.ebantis.com/aiapi/v1.0/activitydetails'
HEADERS = {'Content-Type': 'application/json'}

# Logging configuration
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Async function to fetch activity details
def get_activity_details(employee_transaction_id: int):
    # Get the current date and time
    current_time = datetime.now()
    from_date = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    to_date = current_time.replace(hour=23, minute=59, second=59, microsecond=0)

    # Prepare the API body
    body = {
        "fromDate": from_date.isoformat(),
        "toDate": to_date.isoformat(),
        "employeeTransactionId": employee_transaction_id,
    }

    # Make the API request
    response = requests.post(API_URL, json=body, headers=HEADERS, verify=False)
    if response.status_code == 200:
        return response.json()  # Return the API response as a dictionary
    else:
        return None

# Command handler for /start
async def start(update: Update, context):
    await update.message.reply_text('Hello! Please provide your employee transaction ID.')

# Handle transaction ID input
async def handle_transaction_id(update: Update, context):
    try:
        employee_transaction_id = int(update.message.text)  # Get employeeTransactionId from user input
        data = get_activity_details(employee_transaction_id)

        if data:
            # Format and send the response
            activity_details = data.get('ActivityDetails', {})
            productivity_graph = data.get('ProductivityGraph', [])

            response_message = f"Productivity Ratio: {activity_details.get('ProductivityRatio', 'N/A')}%\n"
            response_message += f"Total Time: {activity_details.get('totalTime', 'N/A')}\n"
            response_message += f"Active Time: {activity_details.get('ActiveTime', 'N/A')}\n"
            response_message += f"Undefined Time: {activity_details.get('UndefinedTime', 'N/A')}\n\n"

            for entry in productivity_graph:
                response_message += f"Date: {entry.get('productivityDate', 'N/A')}\n"
                for data in entry.get('collectedData', []):
                    response_message += f"Start Time: {data.get('StartTime', 'N/A')} | Duration: {data.get('Duration', 'N/A')}s\n"

            await update.message.reply_text(response_message)
        else:
            await update.message.reply_text('No data found for the provided employee transaction ID.')
    except ValueError:
        await update.message.reply_text('Please send a valid employee transaction ID (number).')

# Telegram webhook handler
@app.route('/webhook', methods=['POST'])
async def webhook():
    # Get incoming Telegram updates and process them
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, bot=application.bot)
    await application.process_update(update)
    return 'OK', 200

# Setup the bot and webhook
async def main():
    global application
    application = Application.builder().token(TOKEN).build()

    # Register command and message handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction_id))

    # Set the webhook
    webhook_url = 'https://eba-bot-v1.onrender.com/webhook'
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

# Start Flask and bot together
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    # Run the Flask app
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))
