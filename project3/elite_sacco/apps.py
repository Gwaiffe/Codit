from django.apps import AppConfig


class EliteSaccoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'elite_sacco'
    '''
{% extends "base.html" %}
{%load django_bootstrap5%}
{% block page_header %}
<div class="p-3 mb-4 bg-light border rounded-3">
    <div class="container-fluid py-4">
        <h1 class="display-3"><b>Dashboard</b></h1>
        <p class="lead">Welcome to Elite Saving SACCO Management System.</p>
        <p class="lead">This is the main dashboard.</p>
    </div>
</div>
{% endblock page_header %}'''
