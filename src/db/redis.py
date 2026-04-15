# uses  structure key-value,fast,we fetch data from db like postgres for token storage, caching(get/post),
#  we can do that much faster using redis as temporary storage/ work so we fetch data faster
# we can also limit reuest counts for users to avoid spam
# we make connection client to redis server, sen command to reddis, it fetch details and return in bytes.
# we use docker to run reddis it provides cleanliness and easy,
# we store data in reddis 1- without expiry- data stays in memory unless redis restart/delete manually
# 2-with expiry automatic delete after set expiry and this is used for tokens,cache,sessions etc

import redis.asyncio as aioredis
from src.config import Config

jti_expiry= 3600

token_blocklist = aioredis.from_url(Config.REDIS_URL, decode_responses=True)
# this url will have redisname=docker exposes redis to machine as localhost, port=6379, /0=database

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=jti_expiry)

async def token_in_blockedlist(jti:str) ->bool:
    jti = await token_blocklist.get(jti)

    return jti is not None




