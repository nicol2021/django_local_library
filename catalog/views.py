from django.shortcuts import render

# Create your views here.

from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin


# ------------------------------
# If you're using function-based views, the easiest way to restrict access to your functions is to apply the login_required decorator to your view function
# from django.contrib.auth.decorators import login_required
@login_required
# ------------------------------

# ------------------------------
# разрешения (permissions) для функций в представлении
# from django.contrib.auth.decorators import permission_required
@permission_required('catalog.can_mark_returned')
@permission_required('catalog.can_edit')
# ------------------------------

def index(request):
   """
   Функция отображения для домашней страницы сайта.
   """
   # Генерация "количеств" некоторых главных объектов
   num_books=Book.objects.all().count()
   num_instances=BookInstance.objects.all().count()
   # Доступные книги (статус = 'a')
   num_instances_available=BookInstance.objects.filter(status__exact='a').count()
   num_authors=Author.objects.count()  # Метод 'all()' применён по умолчанию.

   # домашнее задание (ДЗ)
   num_genres=Genre.objects.all().count()
   num_books_title=Book.objects.filter(title='Earth hour').count()

   # Отрисовка HTML-шаблона index.html с данными внутри
   # переменной контекста context
   # return render(
   #    request,
   #    'index.html',
   #    context={'num_books':num_books,'num_books_title':num_books_title,'num_genres':num_genres,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors},
   # )

   num_authors=Author.objects.count()  # The 'all()' is implied by default.

   # Number of visits to this view, as counted in the session variable.
   num_visits=request.session.get('num_visits', 0)
   request.session['num_visits'] = num_visits+1

   # Render the HTML template index.html with the data in the context variable.
   return render(
      request,
      'index.html',
      context={'num_books':num_books,'num_authors':num_authors,'num_genres':num_genres,'num_instances':num_instances,'num_instances_available':num_instances_available,
         'num_visits':num_visits}, # num_visits appended
   )


# from django.views import generic

class BookListView(generic.ListView):
   model = Book
   paginate_by = 10

# -----------------------------
# the easiest way to restrict access to logged-in users in your class-based views is to derive from LoginRequiredMixin. You need to declare this mixin first in the superclass list, before the main view class.
# from django.contrib.auth.mixins import LoginRequiredMixin
# -----------------------------
# class BookDetailView(generic.DetailView):

class BookDetailView(LoginRequiredMixin,generic.DetailView):
   model = Book

class AuthorListView(generic.ListView):
   model = Author
   paginate_by = 10

# ------------------------------
# разрешение (permissions) mixin для представлений на основе классов
# from django.contrib.auth.mixins import PermissionRequiredMixin
# ------------------------------
# class AuthorDetailView(generic.DetailView):

class AuthorDetailView(PermissionRequiredMixin, generic.DetailView):

   # ------------------------------
   permission_required = 'catalog.can_mark_returned'
   # Or multiple permissions
   # permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
   # Note that 'catalog.can_edit' is just an example
   # the catalog application doesn't have such permission!
   # ------------------------------

   model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
   """
   Generic class-based view listing books on loan to current user.
   """
   model = BookInstance
   template_name ='catalog/bookinstance_list_borrowed_user.html'
   paginate_by = 10

   def get_queryset(self):
      return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooks_ForStaff_ListView(PermissionRequiredMixin, generic.ListView):
   """
   Generic class-based view listing books on loan to staff.
   """
   permission_required = 'catalog.can_mark_returned'
   model = BookInstance
   template_name ='catalog/bookinstance_list_borrowed_staff.html'
   paginate_by = 10

   def get_queryset(self):
      return BookInstance.objects.filter(status__exact='o').order_by('due_back')


# ----------------Django Tutorial Part 9: Working with forms--------------------
#--------https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms

from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})


# -------------------------------------------------------------------------------------------------------------

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
# from .models import Author

class AuthorCreate(CreateView):
   model = Author
   fields = '__all__'
   initial={'date_of_death':'2017-11-27',}

class AuthorUpdate(UpdateView):
   model = Author
   fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
   model = Author
   success_url = reverse_lazy('authors')


# -------------------------------------------------------
# from .models import Book

class BookCreate(CreateView):
    model = Book
    fields = '__all__'
   #  initial={'......',}

class BookUpdate(UpdateView):
    model = Book
    fields = ['title','summary','isbn','genre']

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')

