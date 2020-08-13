from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from pheme.parser.xml import XMLParser


@api_view(['POST'])
@parser_classes([XMLParser])
def report(request):
    return Response(request.data)
