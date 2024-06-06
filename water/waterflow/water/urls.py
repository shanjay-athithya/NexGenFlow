from django.urls import path
from .views import *


urlpatterns = [
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('home/', home_view, name='home'),
    path('logout/', logout_view, name='logout'),  #  # Redirect to 'login' after logout
    path('about/', about_view, name='about'),
    path('network/', network_visualization, name='network_visualization'),
    path('network_management/', network_management, name='network_management'),
    path('create_node/', create_node, name='create_node'),
    path('create_edge/', create_edge, name='create_edge'),
    path('edit_node/<int:node_id>/', edit_node, name='edit_node'),
    path('edit_edge/<int:edge_id>/', edit_edge, name='edit_edge'),
    path('delete_node/<int:node_id>/', delete_node, name='delete_node'),
    path('delete_edge/<int:edge_id>/', delete_edge, name='delete_edge'),
    path('optimization/', optimization_page, name='optimization_page'),
    path('contact-us/', contact_us, name='contact_us'),
]
