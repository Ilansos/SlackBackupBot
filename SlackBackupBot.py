import os
from slack_sdk import WebClient
import logging
import json
import time
import slack_sdk.errors
import sys

# Set up the logging configuration
logging.basicConfig(stream=sys.stdout, 
                    level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SLACK_API_KEY = os.getenv('SLACK_API_KEY')
CHANNELS = os.getenv('CHANNELS')

# Initialize a WebClient instance
client = WebClient(token=SLACK_API_KEY)

def get_sender_info(message):
    # Get sender's username or ID
    user_id = message.get("user")
    #print(user_id)
    if user_id:
        user_info = client.users_info(user=user_id)
        #print(user_info)
        if user_info["ok"]:
            if user_info['user']['name'] == "test_app":
                return ""
            else:
                return f"@{user_info['user']['name']}"
        else:
            return f"<@{user_id}>"
    else:
        return "Unknown Sender"

def format_message(message, sender_info):
    if sender_info == "":
        message_text = f"{message.get('text', '')}"
    else:
        message_text = f"{sender_info}: {message.get('text', '')}"
    
    if "files" in message:
        for file in message["files"]:
            message_text += f"\nFile: {file['permalink']}"
    
    return message_text.strip() 

def copy_messages(source_channel, destination_channel):
    # Fetch messages from the source channel
    result = client.conversations_history(channel=source_channel)
    messages = result["messages"]
    
    # Reverse the order of messages
    messages.reverse()
    
    # Post fetched messages to the destination channel
    for message in messages:
        sender_info = get_sender_info(message)
        message_text = format_message(message, sender_info)
        if message_text.strip():  # If there is any content to post
            client.chat_postMessage(channel=destination_channel, text=message_text)
            time.sleep(1)

def main():
    channels_ids = json.loads(CHANNELS)
    source_channels = channels_ids  # Replace with the ID of the source channel
    destination_channels = channels_ids  # Replace with the ID of the destination channel
    for source_channel, destination_channel in zip(source_channels, destination_channels):
        try:
            # Call the function to copy messages
            copy_messages(source_channel, destination_channel)
        except Exception as e:
            logger.error(e)
            continue
    logger.info("Finished copying all the messages.")
    
if __name__ == "__main__":
    main()