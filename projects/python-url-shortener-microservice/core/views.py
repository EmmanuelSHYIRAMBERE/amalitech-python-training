from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    def get(self, request):
        connection.ensure_connection()
        return Response({"status": "ok", "db": "reachable"})
