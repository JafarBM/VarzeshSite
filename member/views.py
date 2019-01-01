# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from member.models import CreditLog


@login_required
def credit_log(request):
    student = request.user.student
    logs = CreditLog.objects.filter(student=student)
    return render(
        request=request,
        template_name='credit_log.html',
        context={'logs': logs}
    )
