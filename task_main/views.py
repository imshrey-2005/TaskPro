from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer,JSONRenderer
from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from rest_framework.response import Response
from .models import Tasks
from .serializers import TaskListCreateSerializer,TaskEditSerializer,TaskCreateSerializer
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



# Create your views here.
class TaskListView(mixins.ListModelMixin,GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskListCreateSerializer
    renderer_classes=[TemplateHTMLRenderer,JSONRenderer]
    
    
    def get_queryset(self):
        queryset = Tasks.objects.filter(user=self.request.user).order_by('expiry') 
        status = self.request.query_params.get('status') 
        sortby = self.request.query_params.get('sortby') 
        if status: 
            queryset = queryset.filter(status=status) 
        else: 
            queryset = queryset.exclude(status='done') 
            if sortby: 
                print(sortby) 
                queryset = queryset.order_by(sortby) 
        return queryset
    
    def get(self, request, *args, **kwargs):
        serializer=self.get_serializer(self.get_queryset(), many=True)
        return Response({'tasks': serializer.data}, template_name='task_main/tasklist.html')
 

class TaskCreateView(mixins.CreateModelMixin,GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskCreateSerializer
    renderer_classes=[TemplateHTMLRenderer,JSONRenderer]

    def get(self, request, *args, **kwargs):
        return Response({}, template_name='task_main/task_create.html')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,partial=True)
        if serializer.is_valid():
            messages.success(request, 'Task created successfully!')
            serializer.save(user=request.user)
            return HttpResponseRedirect(reverse('tasklist'))
        return Response({'errors': serializer.errors}, template_name='task_main/task_create.html')

    
class TaskEditView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskEditSerializer
    renderer_classes=[TemplateHTMLRenderer,JSONRenderer]
    lookup_field='slug'
    lookup_url_kwarg='slug'
    template_name='task_main/task_edit.html'
    

    def get_queryset(self):
        return Tasks.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()  
        serializer = self.get_serializer(instance)
        return Response({'task': serializer.data}, template_name=self.template_name)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            messages.success(request, 'Task updated successfully!')
            self.perform_update(serializer)
            return HttpResponseRedirect(reverse('tasklist'))
        return Response({'object': serializer.data, 'errors': serializer.errors}, template_name=self.template_name)


class TaskDeleteView(mixins.DestroyModelMixin,GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskListCreateSerializer
    renderer_classes=[TemplateHTMLRenderer,JSONRenderer]
    queryset=Tasks.objects.all()
    lookup_field='slug'
    lookup_url_kwarg='slug'
    template_name='task_main/task_delete_confirm.html'

    def get_queryset(self):
        return Tasks.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer=self.get_serializer(instance)
        return Response({'object': serializer.data}, template_name=self.template_name)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        messages.success(request, 'Task deleted successfully!')
        return HttpResponseRedirect(reverse('tasklist'))

class TaskToggleView(GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskListCreateSerializer
    renderer_classes=[TemplateHTMLRenderer,JSONRenderer]
    queryset=Tasks.objects.all()
    lookup_field='slug'
    lookup_url_kwarg='slug'

    def get_queryset(self):
        return Tasks.objects.filter(user=self.request.user)

 
    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'pending':
            instance.status = 'done'
        else:
            instance.status = 'pending'
        instance.save()
        messages.success(request, 'Task status toggled successfully!')
        return HttpResponseRedirect(reverse('tasklist'))

class TaskSearchView(mixins.ListModelMixin, GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=TaskListCreateSerializer
    renderer_classes=[TemplateHTMLRenderer,JSONRenderer]
    template_name='task_main/tasklist.html'

    def get_queryset(self):
        queryset = Tasks.objects.filter(user=self.request.user).order_by('expiry')
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset

    def get(self, request, *args, **kwargs):
        serializer=self.get_serializer(self.get_queryset(), many=True)
        return Response({'tasks': serializer.data}, template_name=self.template_name)
