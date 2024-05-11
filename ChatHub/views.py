from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import MessageForm
from .models import ChatChannel, ChatMessage
from django.contrib.auth.decorators import login_required
from ModelForge.views import resx
import uuid

def home(request):
    return render(request, 'ChatHub/home.html', {'user': request.user})

@login_required
def create_chat_channel_button(request):
    if request.method == 'POST':
        chat_name = request.POST.get('chat_name')
        if not chat_name:
            return render(request, 'ChatHub/create_chat_channel.html', {'error_message': 'Please provide a chat name.'})
        chat_channel = ChatChannel.objects.create(chat_name=chat_name, user=request.user, chat_uuid=uuid.uuid4())
        return redirect('chat_interface', chat_channel_uuid=chat_channel.chat_uuid)
    return render(request, 'ChatHub/create_chat_channel.html', {})

@login_required
def chat_interface(request, chat_channel_uuid):
    try:
        chat_channel = get_object_or_404(ChatChannel, chat_uuid=chat_channel_uuid)
    except Http404:
        return JsonResponse({'message': 'Invalid chat channel UUID.'})
    chat_channels_list = ChatChannel.objects.all()
    chat_messages = chat_channel.chat_messages.all()
    form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message_user = form.save(commit=False)
            message_user.user = request.user
            message_user.chat = chat_channel
            message_user.save()

            # AI response
            ai_response_text = resx(message_user.text)
            ai_message = ChatMessage(user=request.user, text=ai_response_text, is_user_message=False, chat=chat_channel)
            ai_message.save()
            return redirect('chat_interface', chat_channel_uuid=chat_channel.chat_uuid)

    return render(request, 'ChatHub/chatInterface.html', {
        'chat_messages': chat_messages,
        'form': form,
        'chat_channel': chat_channel,
        'chat_channels_list': chat_channels_list
    })

@login_required
def delete_chat(request, chat_uuid):
    try:
        chat_channel = get_object_or_404(ChatChannel, chat_uuid=chat_uuid)
        chat_channel.delete()
        return JsonResponse({'message': 'Chat channel deleted successfully'})
    except Http404:
        return JsonResponse({'message': 'Chat channel not found.'})