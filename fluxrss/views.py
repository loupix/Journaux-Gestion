import math
from rest_framework.response import Response
from rest_framework import status, generics
from fluxrss.models import FluxRssModel
from fluxrss.serializers import FluxRssSerializer


# Create your views here.


class FluxRssView(generics.GenericAPIView):
    serializer_class = FluxRssSerializer
    queryset = FluxRssModel.objects.all()

    def get(self, request):
        page_num = int(request.GET.get("page", 1))
        limit_num = int(request.GET.get("limit", 10))
        start_num = (page_num - 1) * limit_num
        end_num = limit_num * page_num
        search_param = request.GET.get("search")
        values = FluxRssModel.objects.all()
        total_values = values.count()
        if search_param:
            values = values.filter(title__icontains=search_param)
        serializer = self.serializer_class(values[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_values,
            "page_num": page_num,
            "total_page": math.ceil(total_values / limit_num),
            "data": serializer.data
        })


    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"value": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)








class FluxRssViewDetail(generics.GenericAPIView):
    queryset = FluxRssModel.objects.all()
    serializer_class = FluxRssSerializer

    def get_fluxRss(self, id):
        try:
            return FluxRssModel.objects.get(id=id)
        except:
            return None

    def get(self, request, id):
        fluxRss = self.get_fluxRss(id=id)
        if fluxRss == None:
            return Response({"status": "fail", "message": f"fluxRss with Id: {id} not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(fluxRss)
        return Response({"status": "success", "data": {"fluxRss": serializer.data}})

    def patch(self, request, id):
        fluxRss = self.get_fluxRss(id)
        if fluxRss == None:
            return Response({"status": "fail", "message": f"fluxRss with Id: {id} not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            fluxRss, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.validated_data['updatedAt'] = datetime.now()
            serializer.save()
            return Response({"status": "success", "data": {"fluxRss": serializer.data}})
        return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        fluxRss = self.get_fluxRss(id)
        if fluxRss == None:
            return Response({"status": "fail", "message": f"value with Id: {id} not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            fluxRss, data=request.data, partial=True)

        if serializer.is_valid():
            data = serializer.data
            fluxRss.delete()
            return Response({"status": "success", "data": {"value": data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)




