from django.shortcuts import render
from django.views.generic import ListView
from .models import Tasks


# Create your views here.
class TaskListView(ListView):
    model = Tasks
    template_name = 'task_main/tasklist.html'
    context_object_name='tasks'
    def get_queryset(self):
        return Tasks.objects.filter(user=self.request.user)
    
class TaskCreateView():
    pass
class TaskEditView():
    pass
class TaskDeleteView():
    pass
class TaskFilterByStatus():
    pass
