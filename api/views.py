from time import time

from rest_framework.response import Response
from rest_framework.views import APIView

from api.exceptions import wrap_exception
from api.redis_db import RedisWrapper
from api.serializers import DomainFilterSerializer, DomainSaveSerializer


class VisitedDomainsAPIView(APIView):
    http_method_names = ["get"]

    @wrap_exception
    def get(self, request):
        serializer = DomainFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        visited_domains = RedisWrapper().get_visited_domains(serializer.data["from"], serializer.data["to"])
        return Response({"status": "ok", "domains": visited_domains})


class VisitedLinksAPIView(APIView):
    http_method_names = ["post"]

    @wrap_exception
    def post(self, request):
        receive_ts = time()
        serializer = DomainSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        RedisWrapper().set_visited_domains(serializer.data["links"], receive_ts)
        return Response({"status": "ok"})
