from django.test import TestCase

# Create your tests here.

'''
<p><a href="{% url 'learning_logs:home_page' %}">Learning Logs</a>-
        <a href="{% url 'learning_logs:topics' %}">Topics</a>-
        {% if user.is_authenticated%}
        HELLO...{{user.username}}
        {% else %}
        <a href="{% url 'accounts:register' %}">Register</a> -
        <a href="{% url 'accounts:login' %}">
            Log in</a>
        {% endif %}
    </p>
'''
