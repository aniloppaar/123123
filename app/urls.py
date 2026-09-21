from django.urls import path
from . import views

urlpatterns = [
    path('users', views.UsersView.as_view()),

    path('categories', views.CategoriesView.as_view()),
    path('categories/<int:pk>/quotes', views.CategoryQuotesView.as_view()),

    path('quotes', views.QuotesView.as_view()),
    path('quotes/random', views.QuoteRandomView.as_view()),
    path('quotes/<int:pk>', views.QuoteDetailView.as_view()),
]