from datetime import datetime

import pytest
from django.conf import settings
from django.test import Client, override_settings
from django.urls import reverse_lazy
from redis import Redis

from api.redis_db import RedisWrapper


class TestApiViews:
    @pytest.fixture(autouse=True)
    def flush_redis(self):
        redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        redis.delete("links")
        self.client = Client()

    def test_visited_links_view_success(self):
        url = reverse_lazy("api:visited_links")
        response = self.client.post(
            url,
            data={
                "links": [
                    "https://ya.ru",
                    "https://ya.ru?q=123",
                    "funbox.ru",
                    "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor",
                ]
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert sorted(RedisWrapper().get_visited_domains()) == sorted(("ya.ru", "stackoverflow.com", "funbox.ru"))

    @pytest.mark.parametrize(
        "payload",
        [
            ("",),
            [],
            ("test", "invalid"),
            # was no instructions whether allow full request be processed if one domain is invalid
            # so i decided to terminate entire request if validation fails
            ("https://ya.ru/", ""),
        ],
    )
    def test_visited_links_view_failed(self, payload):
        url = reverse_lazy("api:visited_links")
        response = self.client.post(url, data={"links": payload}, content_type="application/json")
        assert response.status_code == 400
        assert len(RedisWrapper().get_visited_domains()) == 0

    @pytest.mark.parametrize(
        "domains,ts",
        [
            (["ya.ru", "funbox.ru"], datetime(2020, 4, 8, 12, 12, 12).timestamp()),
            (["stackoverflow.ru"], datetime(2020, 4, 8, 12, 12, 15).timestamp()),
        ],
    )
    def test_visited_domains_view_success(self, domains, ts):
        url = reverse_lazy("api:visited_domains")
        RedisWrapper().set_visited_domains(domains, ts)
        response = self.client.get(url, {"from": ts - 1, "to": ts + 1})
        assert response.status_code == 200
        assert sorted(response.json()["domains"]) == sorted(domains)

    @pytest.mark.parametrize(
        "from_ts,to_ts", [("qweqwe", "qweweq"), ("", "123"), ("123", ""), ("123", "qwe"), ("qwe", "12412")]
    )
    def test_visited_domains_view_failed(self, from_ts, to_ts):
        url = reverse_lazy("api:visited_domains")
        response = self.client.get(url, {"from": from_ts, "to": to_ts})
        assert response.status_code == 400

    @override_settings(REDIS_PORT="10")
    def test_redis_error_handling(self):
        url = reverse_lazy("api:visited_domains")
        response = self.client.get(url, {"from": "1", "to": "1"})
        assert response.status_code == 500
        url = reverse_lazy("api:visited_links")
        response = self.client.post(
            url,
            data={
                "links": [
                    "https://ya.ru",
                    "https://ya.ru?q=123",
                    "funbox.ru",
                    "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor",
                ]
            },
            content_type="application/json",
        )
        assert response.status_code == 500
        assert response.json()["error_details"] == "Redis connection error occurred"
