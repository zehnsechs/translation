import markdown

from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse

from interp.utils import AdminCheckMixin
from interp.models import Task, User

from wkhtmltopdf.views import PDFTemplateView

class Tasks(AdminCheckMixin,View):
    def get(self,request):
        questions = Task.objects.values_list('id', 'title', 'is_published')
        user = User.objects.get(username=request.user.username)
        return render(request, 'tasks.html', context={'questions': questions,'language': user.credentials()})


    def post(self, request):
        title = request.POST['title']
        new_task = Task.objects.create(title=title)
        return redirect(to= reverse('edittask',kwargs = {'id': new_task.id}))


class EditTask(AdminCheckMixin,View):
    def get(self,request,id):
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        if (task.is_published == False):
            is_published = 'false'
        else:
            is_published = 'true'

        return render(request,'editor-task.html', context={'content' : task.get_latest_text() ,'title':task.title,'is_published':is_published, 'taskId':id,'language':str(user.language.name + '-' + user.country.name)})

class SaveTask(AdminCheckMixin,View):
    def post(self,request):
        id = request.POST['id']
        content = request.POST['content']
        print(content)
        is_published = request.POST['is_published']
        title = request.POST['title']
        task = Task.objects.get(id=id)
        if(is_published == 'true'):
            task.is_published = True
        task.title = title
        task.save()
        task.add_version(content)
        return HttpResponse("done")


class TaskVersions(LoginRequiredMixin,View):
    def get(self,request,id):
        task = Task.objects.get(id=id)
        versions_values = task.versions.all().values('text','create_time')
        return JsonResponse(dict(versions=list(versions_values)))

class GetTaskPDF(LoginRequiredMixin, PDFTemplateView):
    filename = 'my_pdf.pdf'
    template_name = 'pdf_template.html'
    cmd_options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'zoom': 15,
        'javascript-delay': 500,
    }

    def get_context_data(self, **kwargs):
        md = markdown.Markdown(extensions=['mdx_math'])
        context = super(GetTaskPDF, self).get_context_data(**kwargs)
        task_id = self.request.GET['id']
        task = Task.objects.filter(id=task_id).first()
        if task is None or task.is_published is False:
            # TODO
            return None

        self.filename = "%s-%s" % (task.title, 'original')
        content = task.get_latest_text()
        context['direction'] = 'ltr'
        context['content'] = content
        context['title'] = self.filename
        return context
