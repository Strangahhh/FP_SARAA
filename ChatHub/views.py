# chathub/views.py

from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.files.storage import FileSystemStorage

from ModelForge.views import get_chat_completion, resx
from .forms import MessageForm, UploadFileForm
from .models import ChatChannel, ChatMessage
from django.contrib.auth.decorators import login_required
from .chroma_utils import summary
from langchain_community.document_loaders import PyPDFLoader
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
        chat_channel = ChatChannel.objects.get(chat_uuid=chat_channel_uuid, user=request.user)
    except ChatChannel.DoesNotExist:
        return JsonResponse({'message': 'Invalid chat channel UUID.'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

    chat_channels_list = ChatChannel.objects.filter(user=request.user)
    chat_messages = chat_channel.chat_messages.all()
    message_form = MessageForm()
    upload_form = UploadFileForm()

    if request.method == 'POST':
        if 'text' in request.POST:
            message_form = MessageForm(request.POST)
            if message_form.is_valid():
                message_user = message_form.save(commit=False)
                message_user.user = request.user
                message_user.chat = chat_channel
                message_user.save()
                chat_completion = get_chat_completion(chat_channel_uuid, request.user)
                ai_response_text = resx(chat_completion)
                ai_message = ChatMessage(user=request.user, text=ai_response_text, is_user_message=False, chat=chat_channel)
                ai_message.save()
                
                return redirect('chat_interface', chat_channel_uuid=chat_channel.chat_uuid)
        
        elif 'file' in request.FILES:
            upload_form = UploadFileForm(request.POST, request.FILES)
            if upload_form.is_valid():
                file = request.FILES['file']
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                file_path = fs.path(filename)
                loader = PyPDFLoader(file_path)
                document = loader.load()
                context_text = "\n\n".join([doc.page_content for doc in document])
                
                summy = summary(context_text)
                
                message_user = ChatMessage(user=request.user, text=filename, is_user_message=True, chat=chat_channel)
                message_user.save()
                
                ai_message = ChatMessage(user=request.user, text=f"""{summy}""", is_user_message=False, chat=chat_channel)
                ai_message.save()
                
                return redirect('chat_interface', chat_channel_uuid=chat_channel.chat_uuid)

    return render(request, 'ChatHub/chatInterface.html', {
        'chat_messages': chat_messages,
        'message_form': message_form,
        'upload_form': upload_form,
        'chat_channel': chat_channel,
        'chat_channels_list': chat_channels_list
    })

@login_required
def delete_chat(request, chat_uuid):
    try:
        chat_channel = get_object_or_404(ChatChannel, chat_uuid=chat_uuid)
        other_chats = ChatChannel.objects.filter(user=request.user).exclude(chat_uuid=chat_uuid)

        chat_channel.delete()

        if other_chats.exists():
            redirect_url = reverse('chat_interface', kwargs={'chat_channel_uuid': other_chats.first().chat_uuid})
            return JsonResponse({'message': 'Chat channel deleted successfully', 'redirect': redirect_url})
        else:
            new_chat = ChatChannel.objects.create(chat_name='Default Chat', user=request.user, chat_uuid=uuid.uuid4())
            redirect_url = reverse('chat_interface', kwargs={'chat_channel_uuid': new_chat.chat_uuid})
            return JsonResponse({'message': 'Chat channel deleted and new chat created', 'redirect': redirect_url})

    except Http404:
        return JsonResponse({'message': 'Chat channel not found.'}, status=404)
