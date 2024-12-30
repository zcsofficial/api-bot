import logging
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import asyncio

# Flask app setup
app = Flask(__name__)

# Replace this with your Bot's API Token
TOKEN = '7772489059:AAFOWyMsWPVy78lwLd7mOxoiCA-CXtJNX7M'

# API Endpoint and Headers for activity details
API_URL = 'https://ebantisaiapi.ebantis.com/aiapi/v1.0/activitydetails'
HEADERS = {'Content-Type': 'application/json'}

# This will handle the webhooks
async def set_webhook(application):
    webhook_url = 'https://eba-bot-v1.onrender.com/webhook'
    await application.bot.set_webhook(url=webhook_url)

# Define the activity details API call
def get_activity_details(employee_transaction_id: int):
    from datetime import datetime
    # Get the current date and time
    current_time = datetime.now()
    from_date = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    to_date = current_time.replace(hour=23, minute=59, second=59, microsecond=0)

    body = {
        "fromDate": from_date.isoformat(),
        "toDate": to_date.isoformat(),
        "employeeTransactionId": employee_transaction_id
    }

    # Make the API request
    response = requests.post(API_URL, json=body, headers=HEADERS, verify=False)
    if response.status_code == 200:
        return response.json()  # Return the API response as a dictionary
    else:
        return None

# Start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hello! Please provide your employee transaction ID.')

# Handle transaction ID and fetch data
def handle_transaction_id(update: Update, context: CallbackContext):
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
            
            update.message.reply_text(response_message)
        else:
            update.message.reply_text('No data found for the provided employee transaction ID.')
    except ValueError:
        update.message.reply_text('Please send a valid employee transaction ID (number).')

# Main function to run the bot
async def main():
    # Set up logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Create the application instance and pass it the bot's token
    application = Application.builder().token(TOKEN).build()

    # Set webhook asynchronously
    await set_webhook(application)

    # Register command and message handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction_id))

    # Start the bot with polling
    await application.run_polling()

# Flask route to handle the webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, application.bot)
    application.process_update(update)
    return 'OK', 200

# Running the app with Flask and asyncio
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))
