import dataclasses

from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from pheme.parser.xml import XMLParser
from pheme.transformation import scanreport


@api_view(['POST'])
@parser_classes([XMLParser])
def report(request):
    return Response(request.data)


@api_view(['POST'])
@parser_classes([XMLParser])
def template(request):
    input_flavour = request.GET.get('flavour', 'gvmd')
    grouping = request.GET.get('grouping')
    if input_flavour == 'gvmd':
        if grouping == 'nvt':
            grouping = scanreport.gvmd.group_by_nvt
        else:
            grouping = scanreport.gvmd.group_by_host

        return Response(
            dataclasses.asdict(
                scanreport.gvmd.transform(request.data, grouping)
            )
        )
    return Response(request.data)
