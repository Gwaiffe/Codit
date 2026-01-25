from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
from . import forms, models
from django.contrib.auth.decorators import login_required


# Create your views here.


def check_topic_owner(request, id):
    topic = models.Topics.objects.get(id=id)
    if topic.owner != request.user:
        raise Http404


def home_page(request):
    return render(request, 'home_page.html')


@login_required
def topics(request):
    topics = models.Topics.objects.filter(owner=request.user).all().values()
    # topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    template = loader.get_template('topics.html')
    context = {'topics': topics}
    return HttpResponse(template.render(context, request))
    # return render(request, 'topics.html', context)


@login_required
def topic(request, topic_id):
    topic = models.Topics.objects.get(id=topic_id)
    # Make sure the topic belongs to the current user.
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('date_c')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'topic.html', context)


@login_required
def new_topic(request):
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = forms.TopicForm()
    else:
        # POST data submitted; process data.
        form = forms.TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')
    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    topic = models.Topics.objects.get(id=topic_id)
    check_topic_owner(request, topic_id)
    if request.method != 'POST':
        form = forms.EntryForm()
    else:
        form = forms.EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    # Display a blank or invalid form.
    context = {'topic': topic, 'form': form}
    return render(request, 'new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = models.Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic.id)
    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = forms.EntryForm(instance=entry)
    else:
        # POST data submitted; process data.
        form = forms.EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
    context = {'entry': entry, 'topic': topic,
               'form': form, }
    return render(request, 'edit_entry.html', context)


def delete_entry(request, entry_id):
    entry = models.Entry.objects.get(id=entry_id)
    topic = entry.topic
    del_entry = get_object_or_404(models.Entry, id=entry_id)
    del_entry.delete()
    context = {'del_entry': del_entry, 'entry': entry, 'topic': topic}
    return redirect('learning_logs:topic', topic_id=topic.id)


def delete_topic(request, topic_id):
    topic = models.Topics.objects.get(id=topic_id)
    del_topic = get_object_or_404(models.Topics, id=topic_id)
    del_topic.delete()
    context = {'topic': topic}
    return redirect('learning_logs:topics')
