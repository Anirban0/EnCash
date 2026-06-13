from rest_framework import serializers


class SmsIngestSerializer(serializers.Serializer):
    raw = serializers.CharField(
        trim_whitespace=False,
        max_length=100_000,
        help_text="Raw SMS alert text, one alert per line.",
    )


class IngestSummarySerializer(serializers.Serializer):
    inserted = serializers.IntegerField()
    duplicates = serializers.IntegerField()
    unparsed = serializers.ListField(child=serializers.CharField())
