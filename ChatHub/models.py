from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class ChatChannel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_channels')
    chat_name = models.CharField(max_length=128)
    chat_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def __str__(self):
        return self.chat_name

class ChatMessage(models.Model):
    chat = models.ForeignKey(ChatChannel, related_name="chat_messages", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_user_message = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Message "{self.text}" from {"User" if self.is_user_message else "AI"} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'