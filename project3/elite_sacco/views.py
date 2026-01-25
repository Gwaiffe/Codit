from django.shortcuts import render, redirect
from . import models


# Create your views here.


def home_page(request):
    return render(request, 'home_page.html')


def members(request):
    members = models.Member.objects.all().values()
    context = {'members': members}
    return render(request, 'members.html', context)


def savings(request, members_id):
    member = models.Member.objects.get(id=members_id)
    savings = member.saving_set.order_by('date')
    context = {'member': member, 'savings': savings}
    return render(request, 'savings.html', context)
