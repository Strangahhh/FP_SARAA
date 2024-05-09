from django.shortcuts import render, redirect, get_object_or_404
from .forms import MessageForm
from .models import ChatChannel
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'ChatHub/home.html', {'user': request.user})

@login_required
def chat_interface(request):
    chat_channel = get_object_or_404(ChatChannel, chat_name='test')
    chat_messages = chat_channel.chat_messages.all()

    form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid:
            message_user = form.save(commit=False)
            message_user.user = request.user
            message_user.chat = chat_channel
            message_user.save()

            #AI response
            return redirect('ChatInterface')
            
    return render(request, 'ChatHub/chatInterface.html', { 'chat_messages': chat_messages, 'form':form})

# @login_required
# def chat_interface(request):
#     user = request.user
#     if request.method == 'POST':
#         form = MessageForm(request.POST)
#         if form.is_valid():
#             user_message_text = form.cleaned_data['message']
#             user_message = ChatMessage(user=user, text=user_message_text, is_user_message=True)
#             user_message.save()

#             # Placeholder for AI response
#             ai_response_text = process_user_message(user_message_text)
#             ai_message = ChatMessage(user=user, text=ai_response_text, is_user_message=False)
#             ai_message.save()

#             # Fetch all messages for display
#             messages = ChatMessage.objects.filter(user=user).order_by('created_at')
#             return render(request, 'ChatHub/chatInterface.html', {'form': form, 'messages': messages})
#     else:
#         form = MessageForm()
#         messages = ChatMessage.objects.filter(user=user).order_by('created_at')
#         return render(request, 'ChatHub/chatInterface.html', {'form': form, 'messages': messages})

def resx(message):
    
    return message