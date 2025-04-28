import redis.asyncio as redis

redis_client = redis.Redis(
    host="centerbeam.proxy.rlwy.net",
    port=50271,
    password="oAlLlywiTdkuwSwSDDMtieMuDkDNsToa",
    decode_responses=True
)
