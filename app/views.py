import json
import random
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Quote, QuoteCategory, User


@method_decorator(csrf_exempt, name='dispatch')
class UsersView(View):
    def get(self, request):
        data = list(User.objects.values('id', 'username', 'email'))
        return JsonResponse(data, safe=False)

    def post(self, request):
        body = json.loads(request.body)
        user = User.objects.create(
            username=body['username'],
            email=body['email'],
        )
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class CategoriesView(View):
    def get(self, request):
        data = list(Category.objects.values('id', 'name'))
        return JsonResponse(data, safe=False)

    def post(self, request):
        body = json.loads(request.body)
        category = Category.objects.create(name=body['name'])
        return JsonResponse({
            'id': category.id,
            'name': category.name,
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class QuotesView(View):
    def get(self, request):
        data = list(
            Quote.objects.annotate(username=F('user__username'))
            .values('id', 'text', 'author', 'username')
        )
        return JsonResponse(data, safe=False)

    def post(self, request):
        body = json.loads(request.body)
        quote = Quote.objects.create(
            text=body['text'],
            author=body.get('author', ''),
            user_id=body.get('user_id'),
        )
        return JsonResponse({
            'id': quote.id,
            'text': quote.text,
            'author': quote.author,
            'username': quote.user.username if quote.user else None,
        }, status=201)


class QuoteDetailView(View):
    def get(self, request, pk):
        quote = get_object_or_404(Quote, pk=pk)
        return JsonResponse({
            'id': quote.id,
            'text': quote.text,
            'author': quote.author,
            'username': quote.user.username if quote.user else None,
        })


class QuoteRandomView(View):
    def get(self, request):
        count = Quote.objects.count()
        if count == 0:
            return JsonResponse({'error': 'Цитат нет'}, status=404)
        quote = Quote.objects.all()[random.randint(0, count - 1)]
        return JsonResponse({
            'id': quote.id,
            'text': quote.text,
            'author': quote.author,
            'username': quote.user.username if quote.user else None,
        })


@method_decorator(csrf_exempt, name='dispatch')
class CategoryQuotesView(View):
    def get(self, request, pk):
        get_object_or_404(Category, pk=pk)
        quote_ids = QuoteCategory.objects.filter(category_id=pk).values_list('quote_id', flat=True)
        data = list(
            Quote.objects.filter(id__in=quote_ids)
            .annotate(username=F('user__username'))
            .values('id', 'text', 'author', 'username')
        )
        return JsonResponse(data, safe=False)

    def post(self, request, pk):
        get_object_or_404(Category, pk=pk)
        body = json.loads(request.body)
        quote_id = body['quote_id']
        get_object_or_404(Quote, pk=quote_id)
        QuoteCategory.objects.get_or_create(quote_id=quote_id, category_id=pk)
        return JsonResponse({'status': 'ok'}, status=201)