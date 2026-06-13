from rest_framework.response import Response
from rest_framework.views import APIView

from .parsers.sms_parser import SmsParser
from .serializers import IngestSummarySerializer, SmsIngestSerializer
from .services.pipeline import run_ingest


class SmsIngestView(APIView):
    """Ingest a block of bank SMS alerts for the authenticated user."""

    throttle_scope = "ingest"

    def post(self, request):
        serializer = SmsIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        summary = run_ingest(
            user=request.user,
            raw=serializer.validated_data["raw"],
            parser=SmsParser(),
        )
        return Response(IngestSummarySerializer(summary).data)
