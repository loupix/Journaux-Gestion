import math
from rest_framework.response import Response
from rest_framework import status, generics
from item.models import ItemModel
from item.serializers import ItemSerializer


# Create your views here.


class ItemView(generics.GenericAPIView):
    serializer_class = ItemSerializer
    queryset = ItemModel.objects.all()

    def get(self, request):
        page_num = int(request.GET.get("page", 1))
        limit_num = int(request.GET.get("limit", 10))
        start_num = (page_num - 1) * limit_num
        end_num = limit_num * page_num
        search_param = request.GET.get("search")
        notes = ItemModel.objects.all()
        total_notes = notes.count()
        if search_param:
            notes = notes.filter(title__icontains=search_param)
        serializer = self.serializer_class(notes[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_notes,
            "page_num": page_num,
            "total_page": math.ceil(total_notes / limit_num),
            "data": serializer.data
        })


    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"value": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)








class ItemViewDetail(generics.GenericAPIView):
    queryset = ItemModel.objects.all()
    serializer_class = ItemSerializer

    def get_item(self, id):
        try:
            return ItemModel.objects.get(id=id)
        except:
            return None

    def get(self, request, id):
        item = self.get_item(id=id)
        if item == None:
            return Response({"status": "fail", "message": f"item with Id: {id} not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(item)
        return Response({"status": "success", "data": {"value": serializer.data}})

    def patch(self, request, id):
        item = self.get_item(id)
        if item == None:
            return Response({"status": "fail", "message": f"item with Id: {id} not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.validated_data['updatedAt'] = datetime.now()
            serializer.save()
            return Response({"status": "success", "data": {"value": serializer.data}})
        return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        item = self.get_item(id)
        if item == None:
            return Response({"status": "fail", "message": f"item with Id: {id} not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            item, data=request.data, partial=True)

        if serializer.is_valid():
            data = serializer.data
            item.delete()
            return Response({"status": "success", "data": {"value": data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)






