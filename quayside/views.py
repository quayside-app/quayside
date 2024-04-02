from django.shortcuts import render
from app.context_processors import global_context


def index(request):
    context = global_context(request)
    userId = context.get("userID")
    if(userId):
        return render(request, "index.html")
    else:
        return render(request, 'welcome.html')
