from django.shortcuts import render


from django.shortcuts import render

def instructions_view(request):
    return render(request, 'instructions.html')

