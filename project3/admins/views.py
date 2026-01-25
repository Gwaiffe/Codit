from django.shortcuts import render, redirect, get_object_or_404
from elite_sacco import models
from .forms import MemberForm, SavingForm
from django.contrib.auth.decorators import login_required
# Create your views here.


def index_page(request):
    return render(request, 'index.html')


@login_required
def new_member(request):
    if request.method != 'POST':
        form = MemberForm()
    else:
        form = MemberForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('admins:member')
    context = {'form': form}
    return render(request, 'new_member.html', context)


@login_required
def new_save(request, member_id):
    member = models.Member.objects.get(id=member_id)
    if request.method != 'POST':
        form = SavingForm()
    else:
        form = SavingForm(data=request.POST)
        if form.is_valid():
            save = form.save(commit=False)
            save.member = member
            save.save()
            return redirect('admins:saving', member_id=member_id)
    context = {'form': form, 'member': member}
    return render(request, 'new_save.html', context)


def member(request):
    members = models.Member.objects.all().values()
    context = {'members': members}
    return render(request, 'member.html', context)


def saving(request, member_id):
    member = models.Member.objects.get(id=member_id)
    savings = member.saving_set.order_by('date')
    context = {'member': member, 'savings': savings}
    return render(request, 'saving.html', context)


def delete_member(request, member_id):
    del_member = get_object_or_404(models.Member, id=member_id)
    del_member.delete()
    return redirect('admins:member')


def delete_save(request, save_id):
    save = models.Saving.objects.get(id=save_id)
    member = save.member
    del_save = get_object_or_404(models.Saving, id=save_id)
    del_save.delete()
    return redirect('admins:saving', member_id=member.id)


def edit_member(request, member_id):
    member = models.Member.objects.get(id=member_id)
    if request.method != 'POST':
        form = MemberForm(instance=member)
    else:
        form = MemberForm(instance=member, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('admins:member')
    context = {'member': member, 'form': form}
    return render(request, 'edit_member.html', context)
