from django.db import models
from accounts.models import CustomUser
from django.utils.text import slugify
#title, description, due date, priority, status
priority_choices=[('Critical','10'),('High', '8'),('Medium', '6'),('Low', '4'),('Lowest', '2')]
status_choices=[('pending','PENDING'),('in progress','IN PROGRESS'),('done','DONE')]
# Create your models here.
class Tasks(models.Model):
    title=models.CharField(max_length=50,)
    slug=models.SlugField(max_length=255,unique=True)
    description=models.CharField(max_length=255)
    expiry=models.DateField()
    priority=models.CharField(max_length=10,choices=priority_choices,default='Lowest')
    status=models.CharField(choices=status_choices,default='pending')
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Tasks.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
