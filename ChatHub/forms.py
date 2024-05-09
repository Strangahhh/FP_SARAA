from django import forms
from django.forms import ModelForm, TextInput
from .models import *

class MessageForm(ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['text']
        widgets = {
            'text': TextInput(attrs={
                'placeholder': 'Ask anything...',
                'class': 'input-area-x',
                'autocomplete': 'off'
            })
        }