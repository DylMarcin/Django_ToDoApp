from django.shortcuts import render, redirect
from django.views.generic.list import ListView # Import klasy widoku listy
from django.views.generic.detail import DetailView # Import klasy widoku danych
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView # Import klasy tworzenia, zmiany widoku
from django.urls import reverse_lazy # import klasy przekierowującej na inną stronę 
from django.contrib.auth.views import LoginView # Import klasy formularzu logowania
from django.contrib.auth.mixins import LoginRequiredMixin # Import klasy pozwalającej na ustawienie logowania na wymagane
from django.contrib.auth.forms import UserCreationForm # Importowanie formularza towrzenia użytkownika - Django nie ma tego domyślnie
from django.contrib.auth import login

from .models import Task

# Utworzenie widoku logowania
class Login(LoginView):
    template_name = 'base/login.html'
    fields = '__all__' 
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('tasks')

# Utworzenie widoku rejestracji
class RegisterPage(FormView):
    template_name = 'base/register.html'
    # Deklaracja formularza do tworzenia użytkownika, !import na górze
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    # Sprawdzenie czy użytkownik nie jest juz zalogowany 
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    # Jeżeli użttkownik jest zalogowany, przekieruj automatycznie na stronę tasks
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

# Utworzenie widoku Listy Zadań
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    # Wyswietlenie danych przypisanych do użytkownika 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        # Zadeklarowanie zmiennej pobierającej wartość z pola search-area - task_list.html
        search_input = self.request.GET.get('search-area') or ''

        # Sprawdzenie jaka wartość wpisana jest w polu search-area poprzez search_input
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__startswith=search_input)

        context['search_input'] = search_input

        # Zwrócenie pasujących zadań
        return context
    

# Utworzenie widoku Danych Zadania
class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

# Utworzenie widoku Tworzenia Zadania
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task 
    # fields = '__all__' --  Wprowadzenie do formularza wszystkich pól z modelu Task (Zamiast ['title', 'descripiton'...])
    # Przekazanie do formularza zadeklarowanych pól title, description, complete
    fields = ['title', 'description', 'complete']

    # Po wypełnieniu formularza przeniesienie na stronę 'tasks'
    success_url = reverse_lazy('tasks')

    # Metoda pozwalająca na przeglądanie zadań tylko aktywnemu, zalogowanemu użytkownikowi 
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

# Utworzenie widoku Edycji Zadania
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task 
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

# Utworzenie widoku Usunięcia Zadania
class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')