
from typing import Iterable
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser




class Role(models.Model):
    name = models.CharField(max_length=150)
    
    def __str__(self):
        return self.name
    
    

class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=100,blank=True,null=True,unique=True)
    phone = models.CharField(max_length=15,blank=True,null=True)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    date_of_birth = models.DateField(blank=True,null=True)
    address = models.TextField(max_length=250,blank=True,null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.username}"
    
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role,_ = Role.objects.get_or_create(name='Admin')
        super().save(*args, **kwargs)