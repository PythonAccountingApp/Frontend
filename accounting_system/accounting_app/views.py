import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from .models import Category, Transaction, User
from .serializers import CategorySerializer, TransactionSerializer


class LoginSystem(viewsets.ViewSet):
    @api_view(["POST"])
    def register_view(request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            email = data.get("email")
            if username in User.objects.values_list("username", flat=True):
                return JsonResponse({"error": "帳號已存在"}, status=400)
            if username and password and email:
                user = User.objects.create(
                    username=username, password=make_password(password), email=email
                )
                return JsonResponse(
                    {"message": "註冊成功", "username": user.username}, status=201
                )
            else:
                return JsonResponse({"error": "缺少必要欄位"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @api_view(["POST"])
    def login_view(request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "登入成功"}, status=status.HTTP_200_OK)
        elif not User.objects.filter(username=username).exists():
            return Response({"error": "帳號不存在"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "密碼錯誤"}, status=status.HTTP_400_BAD_REQUEST)

    @api_view(["POST"])
    def logout_view(request):
        logout(request)
        return Response({"message": "登出成功"}, status=status.HTTP_200_OK)

    @api_view(["GET"])
    def user_view(request):
        users = User.objects.all()
        data = [{"username": user.username, "email": user.email} for user in users]
        return JsonResponse(data, status=status.HTTP_200_OK, safe=False)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        category_type = request.query_params.get("category_type", None)
        if category_type:
            categories.filter(category_type=category_type)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryGetDeleteUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            category = get_object_or_404(Category, id=id)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "無效的 ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            category = get_object_or_404(Category, id=id)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response({"error": "無效的 ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)

        category = request.query_params.get("category", None)
        start_time = request.query_params.get("start_time", None)
        end_time = request.query_params.get("end_time", None)

        if category:
            transactions = transactions.filter(category=category)
        if start_time:
            transactions = transactions.filter(date__gte=start_time)
        if end_time:
            transactions = transactions.filter(date__lte=end_time)

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionGetDeleteUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            transaction = get_object_or_404(Transaction, id=id, user=request.user)
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "無效的 ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        transaction = get_object_or_404(Transaction, id=id, user=request.user)
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            transaction = get_object_or_404(Transaction, id=id, user=request.user)
            transaction.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response({"error": "無效的 ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
