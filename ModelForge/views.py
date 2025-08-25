from django.shortcuts import render
from ChatHub.models import ChatChannel, ChatMessage
import ollama

def resx(chat_completion):
    response = ollama.chat(model='strangex/saraa-8b-orpo-aunqa', messages=chat_completion)
    return response['message']['content']

def get_chat_completion(chat_channel_uuid, user):
    try:
        chat_channel = ChatChannel.objects.get(chat_uuid=chat_channel_uuid, user=user)
    except ChatChannel.DoesNotExist:
        return []

    chat_messages = ChatMessage.objects.filter(chat=chat_channel).order_by('created_at')
    formatted_messages = []
    for message in chat_messages:
        role = 'user' if message.is_user_message else 'assistant'
        content = message.text
        formatted_messages.append({"role": role, "content": content})
    return formatted_messages