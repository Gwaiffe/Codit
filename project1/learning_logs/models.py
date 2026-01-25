from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Topics(models.Model):
    text = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True)
    date_c = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if len(self.text) > 50:
            return f'{self.text[:50]}...'
        else:
            return f'{self.text}'

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'


class Entry(models.Model):
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE)
    text = models.TextField()
    date_c = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if len(self.text) > 50:
            return f'{self.text[:50]}...'
        else:
            return f'{self.text}'

    class Meta:
        verbose_name = 'Entry'
        verbose_name_plural = 'Entries'


''' The About model has a ForeignKey pointing to the Member model, meaning each About instance is related to a specific Member.
on_delete:
Defines what happens to the related objects when the referenced object is deleted.
Common options:
models.CASCADE: Deletes the related objects when the referenced object is deleted.
models.PROTECT: Prevents deletion of the referenced object if related objects exist.
models.SET_NULL: Sets the ForeignKey to NULL when the referenced object is deleted (requires null=True).
models.SET_DEFAULT: Sets the ForeignKey to its default value when the referenced object is deleted.
models.DO_NOTHING: Takes no action when the referenced object is deleted.
related_name (optional):
Specifies the name of the reverse relationship (how the related model can access this model).
Example:
member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='about_info')
You can access all About instances related to a Member instance using member.about_info.all().
Class Meta in Django Models
The Meta class in Django models is used to define metadata for the model. Metadata provides additional information about the model, such as ordering, verbose names, and database table names.
Common Options in Meta:
verbose_name:
Specifies a human-readable singular name for the model.
Example:
verbose_name = "About"
The admin interface will display "About" instead of "Abouts".
verbose_name_plural:
Specifies a human-readable plural name for the model.
Example:
verbose_name_plural = "About"
The admin interface will display "About" for the plural form instead of "Abouts".
ordering:
Specifies the default ordering of query results for the model.
Example:
ordering = ['joined_date']
Orders results by joined_date in ascending order.
db_table:
Specifies the name of the database table for the model.
Example:
db_table = 'custom_table_name'
unique_together:
Ensures that a combination of fields is unique.
Example:
unique_together = [['f_name', 'l_name']]
abstract:
If set to True, the model becomes abstract and will not create a database table.
Example:
abstract = True
'''
