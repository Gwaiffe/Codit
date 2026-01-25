from elite_sacco.models import Member, Saving
from django import forms


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['full_name', 'phone', 'email', 'active']
        labels = {'full_name': 'Full name', 'phone': 'Telephone',
                  'email': 'Email', 'active': 'Active'}


class SavingForm(forms.ModelForm):
    class Meta:
        model = Saving
        fields = ['amount']
        labels = {'amount': 'Amount'}
