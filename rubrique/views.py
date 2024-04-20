import math
from rest_framework.response import Response
from rest_framework import status, generics
from rubrique.models import RubriqueModel
from rubrique.serializers import RubriqueSerializer




# Create your views here.


class RubriqueView(generics.GenericAPIView):
    serializer_class = RubriqueSerializer
    queryset = RubriqueModel.objects.all()

    def get(self, request):
        page_num = int(request.GET.get("page", 1))
        limit_num = int(request.GET.get("limit", 10))
        start_num = (page_num - 1) * limit_num
        end_num = limit_num * page_num
        search_param = request.GET.get("search")
        values = RubriqueModel.objects.all()
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








class RubriqueViewDetail(generics.GenericAPIView):
    queryset = RubriqueModel.objects.all()
    serializer_class = RubriqueSerializer

    def get_rubrique(self, id):
        try:
            return RubriqueModel.objects.get(id=id)
        except:
            return None

    def get(self, request, id):
        rubrique = self.get_rubrique(id=id)
        if rubrique == None:
            return Response({"status": "fail", "message": f"rubrique with Id: {id} not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(rubrique)
        return Response({"status": "success", "data": {"value": serializer.data}})

    def patch(self, request, id):
        rubrique = self.get_rubrique(id)
        if rubrique == None:
            return Response({"status": "fail", "message": f"rubrique with Id: {id} not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            rubrique, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.validated_data['updatedAt'] = datetime.now()
            serializer.save()
            return Response({"status": "success", "data": {"value": serializer.data}})
        return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        rubrique = self.get_rubrique(id)
        if rubrique == None:
            return Response({"status": "fail", "message": f"rubrique with Id: {id} not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            rubrique, data=request.data, partial=True)

        if serializer.is_valid():
            data = serializer.data
            rubrique.delete()
            return Response({"status": "success", "data": {"value": data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)





