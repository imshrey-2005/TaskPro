from django.urls import path
from . import views
urlpatterns=[
    path('',views.TaskListView.as_view(), name='tasklist'),
    path('create/',views.TaskCreateView.as_view(), name='taskcreate'),
    path('edit/<slug:slug>',views.TaskEditView.as_view(), name='taskedit'),
    path('delete/<slug:slug>',views.TaskDeleteView.as_view(), name='taskdelete'),
    
    
]