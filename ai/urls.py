from django.conf.urls import url

from ai.views import ChatGPTAPIView, DeleteSearchHistoryView

app_name = 'ai'
urlpatterns = [
    url(r'^ask$', ChatGPTAPIView.as_view(), name='askAI'),
    url(r'^deleteChatHistory$', DeleteSearchHistoryView.as_view(), name='deleteChatHistory'),
]
