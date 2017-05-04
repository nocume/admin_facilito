from django.shortcuts import render
from django.shortcuts import get_object_or_404

from status.models import Status
from .models import Project
from .models import ProjectUser
from .forms import ProjectForm
from status.forms import StatusChoiceForm

from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy

from django.contrib import messages
from django.db import transaction

"""
Class
"""
class CreateClass(LoginRequiredMixin, CreateView):
	login_url = 'client:login'
	template_name = 'project/create.html'
	model = Project
	form_class = ProjectForm

	@transaction.atomic
	def create_objects(self):
		self.object.save()
		self.object.projectstatus_set.create( status = Status.get_defult_status() )
		self.object.projectuser_set.create(user= self.request.user, permission_id = 1 )

	def form_valid(self, form):
		self.object = form.save(commit = False)
		self.create_objects()
		return HttpResponseRedirect( self.get_url_project() )

	def get_url_project(self):
		return reverse_lazy('project:show', kwargs = {'slug' : self.object.slug} )

class ListClass(LoginRequiredMixin, ListView):
	login_url = 'client:login'
	template_name = 'project/index.html'

	def get_queryset(self):
		return Project.objects.all()

class ListMyProjectsClass(LoginRequiredMixin, ListView):
	login_url = 'client:login'
	template_name = 'project/mine.html'

	def get_queryset(self):
		return ProjectUser.objects.filter(user = self.request.user)

class ListContributorsClass(ListView):
	template_name = 'project/contributors.html'

	def get_queryset(self):
		project = get_object_or_404(Project, slug=self.kwargs['slug'])
		return ProjectUser.objects.filter(project=project)

class ShowClass(DetailView):
	model = Project
	template_name = 'project/show.html'

	def get_context_data(self, **kwargs):
		context = super(ShowClass, self).get_context_data(**kwargs)
		if not self.request.user.is_anonymous():
			context['has_permission'] = self.object.user_has_permission(self.request.user)

		return context

"""
Functions
"""
@login_required(login_url='client:login')
def edit(request, slug=''):
	project = get_object_or_404(Project, slug=slug)
	
	if not project.user_has_permission(request.user):
		lazy = reverse_lazy('project:show', kwargs={'slug': project.slug})
		return HttpResponseRedirect(lazy)

	form_project = ProjectForm(request.POST or None, instance = project)
	forms_status = StatusChoiceForm(request.POST or None, 
									initial = {'status': project.get_id_status()
								})

	if request.method == 'POST':
		if form_project.is_valid() and forms_status.is_valid():
			selection_id = forms_status.cleaned_data['status'].id

			form_project.save()
			if selection_id != project.get_id_status():
				project.projectstatus_set.create( status_id = selection_id)
			messages.success(request, 'Datos actualizados correctamente')
	context = {
		'form_project': form_project,
		'forms_status': forms_status
	}
	return render(request, 'project/edit.html', context)
