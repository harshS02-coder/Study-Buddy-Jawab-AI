from redis import Redis
from config.settings import REDIS_URL, REDIS_TOKEN

redis_client = Redis.from_url(
    REDIS_URL,
    password=REDIS_TOKEN,
    decode_responses=True
)
