from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Project, Task
from .forms import ProjectForm, TaskForm

@login_required
def active(request):
    qs = Project.objects.select_related('customer').all().order_by('-start_date')
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
            form.save()
            return redirect('projects:active')
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Create'})

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:active')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Edit', 'project': project})

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
