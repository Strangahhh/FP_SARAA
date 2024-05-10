from django import forms
from django.forms import ModelForm, TextInput, FileField
from .models import *

class MessageForm(ModelForm):
    file = FileField(required=False)

    class Meta:
        model = ChatMessage
        fields = ['text']
        widgets = {
            'text': TextInput(attrs={
                'placeholder': 'Ask anything...',
                'class': 'input-area',
                'autocomplete': 'off'
            })
        }