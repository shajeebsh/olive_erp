from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from core.utils import get_user_company

@login_required
def active(request):
    company = get_user_company(request)
    qs = Project.objects.filter(company=company).select_related('customer').order_by('-start_date')
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(customer__company_name__icontains=query))
    context = {'projects': qs, 'query': query}
    return render(request, 'projects/active.html', context)

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.company = get_user_company(request)
            project.save()
            return redirect('projects:active')
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Create'})

@login_required
def project_detail(request, pk):
    company = get_user_company(request)
    project = get_object_or_404(Project.objects.select_related('customer'), pk=pk, company=company)
    tasks = Task.objects.filter(project=project).select_related('assigned_to__user')
    context = {
        'project': project,
        'tasks': tasks
    }
    return render(request, 'projects/project_detail.html', context)

@login_required
def project_edit(request, pk):
    company = get_user_company(request)
    project = get_object_or_404(Project, pk=pk, company=company)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:active')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Edit', 'project': project})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('projects:active')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})

@login_required
def tasks(request):
    qs = Task.objects.select_related('project', 'assigned_to__user').all().order_by('due_date')
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(project__name__icontains=query))
    context = {'tasks': qs, 'query': query}
    return render(request, 'projects/tasks.html', context)

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('projects:tasks')
    else:
        form = TaskForm()
    return render(request, 'projects/task_form.html', {'form': form})

@login_required
def timeline(request):
    projects = Project.objects.all().order_by('start_date')
    return render(request, 'projects/timeline.html', {'projects': projects})

@login_required
def resources(request):
    # This could show resource allocation
    return render(request, 'projects/resources.html')
