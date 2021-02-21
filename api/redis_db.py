from typing import Iterable, Tuple, Union

from django.conf import settings

from redis import Redis, RedisError

from api.exceptions import RedisConnectionError


class RedisWrapper:
    def __init__(self):
        self._redis_client = Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )

    @staticmethod
    def _parse_domain(domain: bytes) -> str:
        return domain.decode("utf-8").split(":")[0]

    def get_visited_domains(
        self, from_ts: Union[float, str] = "-inf", to_ts: Union[float, str] = "+inf"
    ) -> Tuple[str]:
        try:
            raw_elements = self._redis_client.zrangebyscore("links", from_ts, to_ts)
            return tuple(set(map(self._parse_domain, raw_elements)))
        except RedisError as e:
            raise RedisConnectionError(e)

    def set_visited_domains(self, domains: Iterable[str], ts: float) -> bool:
        try:
            for domain in domains:
                # https://redislabs.com/redis-best-practices/time-series/sorted-set-time-series/
                # set value according to redis best practices
                self._redis_client.zadd("links", {f"{domain}:{ts}": ts})
            return True
        except RedisError as e:
            raise RedisConnectionError(e)
