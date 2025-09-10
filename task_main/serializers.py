from rest_framework.serializers import ModelSerializer, ChoiceField
from .models import Tasks, priority_choices,status_choices

class TaskListCreateSerializer(ModelSerializer):
    priority = ChoiceField(choices=priority_choices)
    status=ChoiceField(choices=status_choices)
    
    class Meta:
        model=Tasks
        fields=['title','description','expiry','priority','status']
    
class TaskFilterByStatusSerializer(ModelSerializer):
    pass
