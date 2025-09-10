from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from rest_framework.response import Response
from .models import Tasks
from .serializers import TaskListCreateSerializer
from django.contrib import messages



# Create your views here.
class TaskListView(mixins.ListModelMixin,GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskListCreateSerializer
    renderer_classes=[TemplateHTMLRenderer]
    
    
    def get_queryset(self):
        queryset = Tasks.objects.filter(user=self.request.user).order_by('priority')
        
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response({'tasks': queryset}, template_name='task_main/tasklist.html')

class TaskCreateView(mixins.CreateModelMixin,GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskListCreateSerializer
    renderer_classes=[TemplateHTMLRenderer]

    def get(self, request, *args, **kwargs):
        return Response({}, template_name='task_main/task_create.html')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            messages.success(request, 'Task created successfully!')
            serializer.save(user=request.user)
            # Redirect to task list after successful creation
            return HttpResponseRedirect(reverse('tasklist'))
        return Response({'errors': serializer.errors}, template_name='task_main/task_create.html')

    
class TaskEditView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskListCreateSerializer
    renderer_classes=[TemplateHTMLRenderer]
    queryset=Tasks.objects.all()
    lookup_field='slug'
    lookup_url_kwarg='slug'
    template_name='task_main/task_edit.html'
    

    def get_queryset(self):
        return Tasks.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'object': instance}, template_name=self.template_name)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            messages.success(request, 'Task updated successfully!')
            self.perform_update(serializer)
            return HttpResponseRedirect(reverse('tasklist'))
        return Response({'object': instance, 'errors': serializer.errors}, template_name=self.template_name)


class TaskDeleteView(mixins.DestroyModelMixin,GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskListCreateSerializer
    renderer_classes=[TemplateHTMLRenderer]
    queryset=Tasks.objects.all()
    lookup_field='slug'
    lookup_url_kwarg='slug'
    template_name='task_main/task_delete_confirm.html'

    def get_queryset(self):
        return Tasks.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'object': instance}, template_name=self.template_name)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        messages.success(request, 'Task deleted successfully!')
        return HttpResponseRedirect(reverse('tasklist'))
class TaskFilterByStatusView(mixins.RetrieveModelMixin,GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskListCreateSerializer
    template_name = 'task_main/tasklist.html'
    def get_queryset(self):
        query=Tasks.filter(user=self.request.user)
        status=self.request.query_params.get('status')
        return query.filter(status=status)
    def get(self, request):
        queryset = self.get_queryset()
        status = self.request.query_params.get('status')

        # When using TemplateHTMLRenderer, you don't need to serialize the data.
        # Just pass the queryset directly to the Response context.
        return Response({'tasks': queryset, 'status': status}, template_name=self.template_name)




