import discord
from dotenv import load_dotenv
import os
import pytz
import datetime

load_dotenv(dotenv_path='_Taverna Bot 2.0/res/.env')


def get_pl_timezone():
    dt_utcnow = datetime.datetime.now(tz=pytz.utc)
    dt_pl = dt_utcnow.astimezone(pytz.timezone("Europe/Warsaw"))
    return dt_pl

def get_token() -> str:
    return os.getenv("TOKEN")

def get_test_server_id() -> int:
    return int(os.getenv("TEST_SERVER_ID"))

def get_taverna_server_id() -> int:
    return int(os.getenv("TAVERNA_SERVER_ID"))

def get_application_id() -> int:
    return int(os.getenv("APPLICATION_ID"))

def get_channel_id(channel: str) -> int:
    return int(os.getenv(channel))

class Server(discord.abc.Snowflake):
    def __init__(self, server_id: int, name: str):
        self.name = name
        self.id = server_id

TEST_SERVER = Server(get_test_server_id(), "Serwer Testowy")
TAVERNA_SERVER = Server(get_taverna_server_id(), "Serwer Tawerna")
