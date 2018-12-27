from django import forms
from django.db import transaction
from registration.forms import RegistrationForm, RegistrationFormUniqueEmail

from member.models import Student, Member, University, Major


class RegisterForm(RegistrationFormUniqueEmail):
    university = forms.ModelChoiceField(
        queryset=University.objects.all(),
        label='دانشگاه',
        empty_label="دانشگاه خود را انتخاب کنید",
    )
    major = forms.ModelChoiceField(
        queryset=Major.objects.all(),
        label='رشته',
        empty_label="رشته تحصیلی خود را انتخاب کنید",
    )

    class Meta(RegistrationForm.Meta):
        model = Member
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'university', 'major']

    @transaction.atomic
    def save(self, commit=True):
        member = super().save(commit=False)
        member.is_student = True
        member.save()
        Student.objects.create(member=member,
                               university=self.cleaned_data.get('university'),
                               major=self.cleaned_data.get('major'))
        return member
