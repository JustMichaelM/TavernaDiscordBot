import config
from bot import run_bot
import asyncio
    
if __name__ == '__main__':
    asyncio.run(run_bot(config.get_token()))