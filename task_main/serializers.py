from django.forms import ValidationError
from rest_framework.serializers import ModelSerializer, ChoiceField
from .models import Tasks, priority_choices,status_choices
from django.utils import timezone

class TaskListCreateSerializer(ModelSerializer):
    priority = ChoiceField(choices=priority_choices)
    status=ChoiceField(choices=status_choices)
    
    class Meta:
        model=Tasks
        fields=['title','slug','description','expiry','priority','status']
    
class TaskCreateSerializer(ModelSerializer):
    priority = ChoiceField(choices=priority_choices)
    status=ChoiceField(choices=status_choices)
    class Meta:
        model=Tasks
        fields=['title','description','expiry','priority','status']

    def validate_title(self, value):
        task=Tasks.objects.filter(title=value)
        if Tasks.objects.filter(title=value).exists():
            if task['expiry']<timezone.now():
                task.delete()
            raise ValidationError("Task with this title already exists.")
        return value


class TaskEditSerializer(ModelSerializer):
    priority = ChoiceField(choices=priority_choices)
    status=ChoiceField(choices=status_choices)
    class Meta:
        model=Tasks
        fields=['title','slug','description','expiry','priority','status']

   
