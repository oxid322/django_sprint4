from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)

from .forms import CommentForm
from .models import Post, Category, Comment


class MyLoginView(LoginView):
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    ordering = ['-pub_date']

    def get_queryset(self):
        today = now()
        print(today)
        data = (Post.objects
                .filter(pub_date__lte=today)
                .filter(is_published=True)
                .filter(category__is_published=True)
                .annotate(comment_count=Count('comments'))
                .order_by('-pub_date'))
        return data


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10
    ordering = ['-pub_date']

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = Category.objects.get(slug=category_slug)
        if category.is_published:
            data = (Post.objects
                    .annotate(comment_count=Count('comments'))
                    .filter(category__slug=category_slug)
                    .filter(is_published=True)
                    .filter(pub_date__lte=now()))
            return data
        raise Http404

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Get the category based on the slug from URL
        category_slug = self.kwargs.get('category_slug')
        context['category'] = get_object_or_404(Category,
                                                slug=category_slug,
                                                is_published=True)
        context['page_obj'] = (self
                               .get_queryset()
                               .order_by('-pub_date')[:10])
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (Comment.objects.
                               filter(post=self.object)
                               .order_by('created_at'))
        return context

    def get_object(self, queryset=None):
        if self.kwargs['pk'] == 0:
            self.kwargs['pk'] = 1
        post = super().get_object(queryset)
        if post.author == self.request.user:
            return get_object_or_404(Post,
                                     pk=self.kwargs['pk'])
        obj = get_object_or_404(Post,
                                pk=self.kwargs['pk'],
                                is_published=True,
                                pub_date__lte=now(),
                                category__is_published=True)

        return obj


class UserRegistrationView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title',
              'text',
              'pub_date',
              'category',
              'image']

    def get_form(self, form_class=None):
        form = super().get_form()
        form.instance.author = self.request.user
        return form

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10
    ordering = ['-pub_date']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['profile'] = self.get_object()
        context['page_obj'] = (self.get_queryset()
                               .annotate(comment_count=Count('comments'))
                               .order_by('-pub_date')[:10])
        return context

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        return get_object_or_404(User,
                                 username=username)

    def get_queryset(self):
        user = self.get_object()
        if user == self.request.user:
            return (Post.objects
                    .filter(author__username=user.username)
                    .order_by('-pub_date'))
        return (Post.objects
                .filter(author__username=user.username,
                        is_published=True)
                .order_by('-pub_date'))


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['username',
              'email',
              'first_name',
              'last_name']

    def get_object(self, queryset=None):
        username = self.request.user.username
        return User.objects.get(username=username)

    def get_success_url(self):
        form = self.get_form()
        self.request.user.username = form.instance.username
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title',
              'text',
              'category',
              'image',
              'location']
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()  # Получаем объект поста
        if post.author != request.user:
            return redirect('blog:post_detail',
                            pk=post.pk)
        return super().dispatch(request,
                                *args,
                                **kwargs)

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail',
                        pk=post.pk)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/delete.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail',
                            pk=post.pk)
        return super().dispatch(request,
                                *args,
                                **kwargs)


@login_required
def comment_create(request, pk):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = get_object_or_404(Post,
                                             is_published=True,
                                             pk=pk)
            comment.save()
            return redirect('blog:post_detail',
                            pk=pk)
    form = CommentForm()
    post = get_object_or_404(Post, pk=pk)
    context = {'form': form, 'post': post}
    return render(request,
                  'blog/detail.html',
                  context)


class HasPermissionMixin(LoginRequiredMixin):
    def has_permission(self, user, comment):
        # Логика проверки прав доступа пользователя к комментарию
        return user.is_authenticated and user == comment.author


class CommentDeleteView(HasPermissionMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment = get_object_or_404(Comment,
                                    pk=self.kwargs['comment_id'])
        # Проверка, что пользователь является автором комментария
        if comment.author != self.request.user:
            raise PermissionDenied("Вы не можете"
                                   " удалить этот комментарий.")
        return comment

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.object.post.pk})

    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment,
                                    id=self.kwargs['comment_id'])
        # Проверка прав доступа
        if not self.has_permission(request.user, comment):
            return HttpResponseForbidden()
        return render(request,
                      'blog/comment.html',
                      {'comment': comment})


class CommentUpdateView(HasPermissionMixin,
                        UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )
