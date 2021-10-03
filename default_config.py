"""
default_config.py
Samuel Lee
10/03/2021

config module for bot.py

"""
import json

# reads from config.json
with open("default_config.json") as read_conf:
    config_file = json.load(read_conf)

messages = config_file["stats"]["messages"]
mentions = config_file["stats"]["bot_mentions"]
graceful_end = config_file["stats"]["last_shutdown_graceful"]

token = config_file["env"]["token"]
main_guild = config_file["env"]["guild"]
prefix = config_file["env"]["prefix"]

bound_text_channels = config_file["bot_text_channels"]
message_logging = config_file["env"]["message_logging"]
event_logging = config_file["env"]["event_logging"]
operator = config_file["operator"]

# writes to config.json
def writeout():
    config_file["stats"]["messages"] = messages
    config_file["stats"]["bot_mentions"] = mentions
    config_file["stats"]["last_shutdown_graceful"] = graceful_end

    config_file["env"]["message_logging"]  = message_logging
    config_file["env"]["event_logging"] = event_logging

    config_file["bot_text_channels"] = bound_text_channels

    with open("config.json", "w") as write_conf:
        json.dump(config_file, write_conf, indent="\t")