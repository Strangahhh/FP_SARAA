from django import forms
from django.forms import ModelForm, TextInput
from .models import ChatMessage

class MessageForm(ModelForm):
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

class UploadFileForm(forms.Form):
    file = forms.FileField()