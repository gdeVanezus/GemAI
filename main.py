import disnake
from disnake.ext import commands
from disnake import Intents
import os
from dotenv import load_dotenv
import logging
import logging.handlers
load_dotenv()

logger = logging.getLogger("disnake")
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    filename = "logs/gemai.log",
    encoding = "utf-8",
    maxBytes = 32 * 1024 * 1024, 
    backupCount = 5,
    )
dt_fmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style = "{")
handler.setFormatter(formatter)
logger.addHandler(handler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

token = os.environ["TOKEN"]
INTENTS = Intents.all()


class Bot(commands.AutoShardedInteractionBot):
    def __init__(self):
        super().__init__(
            shard_count=2,
            intents=INTENTS,
            owner_id=['1105120003197522000', '1027979712066236516'],
            reload=True,
            strict_localization=True,
            chunk_guilds_at_startup=False,
        )
        
    def setup(self) -> None:
        try:
            logger.info('[ COGS ] Loading...')
            self.load_extensions('cogs')
            logger.info('[ COGS ] Loaded!')
        except Exception as e:
            logger.error('[ COGS ] ERROR!', e)
        
        
    def run(self) -> None:
        self.setup()
        super().run(token, reconnect=True)
        
        



if __name__ == "__main__":
    logger.info('[ BOT ] Loading...')
    Bot().run()