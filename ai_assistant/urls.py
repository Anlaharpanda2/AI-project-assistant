from django.urls import path
from assistant.views import chat, test_speak, generate_image, image_generator_page

urlpatterns = [
    path('', image_generator_page, name='home'),
    path('chat/', chat, name='chat'),
    path('speak/', test_speak, name='test_speak'),
    path('generate/', generate_image, name='generate'),
]
