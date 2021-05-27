from django.urls import path
from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from .views import SearchResultsView, MyProfileView

app_name = 'roommates'
urlpatterns = [
    path('', TemplateView.as_view(template_name="roommates/login.html"), name='login'),
    path('edit/', views.edit_profile, name='edit'),
    path('browse/', views.ProfileView.as_view(), name='browse'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('favorite/<int:id>/', views.favorite_add, name="favorite_add"),
    path('favorites/', views.favorite_list, name="favorite_list"),
    path('block/<int:id>/', views.block_add, name="block_add"),
    path('blocked/', views.block_list, name="block_list"),
    path('myprofile/', MyProfileView.as_view(), name='my_profile'),
    path('logout/', views.Logout, name="logout"),
    path('filter/', views.filter, name="filter"),
    path('privacy/', views.LegalView.as_view(), name="privacy_policy"),
    path('chat/', views.create_message, name='messages'),
    path('chat/<int:id>/', views.delete_message, name='delete_message'),
]
