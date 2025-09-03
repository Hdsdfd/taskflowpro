from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .models import ProjectFile
from .forms import ProjectFileForm

class ProjectFileListView(LoginRequiredMixin, ListView):
    model = ProjectFile
    template_name = 'files/file_list.html'
    context_object_name = 'files'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ProjectFile.objects.all()
        return ProjectFile.objects.filter(project__members=user).order_by('-uploaded_at')

class ProjectFileDetailView(LoginRequiredMixin, DetailView):
    model = ProjectFile
    template_name = 'files/file_detail.html'
    context_object_name = 'file'

class ProjectFileCreateView(LoginRequiredMixin, CreateView):
    model = ProjectFile
    form_class = ProjectFileForm
    template_name = 'files/file_form.html'
    success_url = reverse_lazy('files:file_list')

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)
