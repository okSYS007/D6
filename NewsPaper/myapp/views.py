
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView 
from django.core.paginator import Paginator 
from django.shortcuts import render, redirect
from django.views import View 
from .models import Post, Category, Appointment, CategorySubscribers, User, Author
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from datetime import date

class PostList(ListView):

    model = Post  
    template_name = 'news.html'
    context_object_name = 'news'
    ordering = ['-creation_date']
    paginate_by = 10 
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context    

class PostDetail(DetailView):
    model = Post 
    template_name = 'article.html'
    context_object_name = 'article' 

class SearchList(ListView):

    model = Post  
    template_name = 'search.html'
    context_object_name = 'search'
    ordering = ['-creation_date']

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset()) 

        #проверка есть ли категория в фильтрах + проверка есть ли эта категория УЖЕ в подписках
        #если у пользователя уже есть в подписках эта категория тогда кнопку можно не показывать
        context['showFollow'] = False
        if self.request.GET.get('category') is not None and not self.userCatExists():
            context['showFollow'] = True
            context['category'] = Category.objects.filter(id = self.request.GET['category']).first

        return context 

    def userCatExists(self):
        Cat =  Category.objects.filter(id = self.request.GET.get('category')).first()
        UserReq =  User.objects.get(username = self.request.user)
        return CategorySubscribers.objects.filter(category = Cat, subscribers = UserReq).exists()

    def post(self, request, *args, **kwargs):
        category = request.GET.get('category')
        if category is not None:
            CatUpdate = Category.objects.get(id = category)
            CatUpdate.subscribers.add(request.user)
            CatUpdate.save()

        return redirect('/news')

class Search(View):

    def get(self, request):
        search = Post.objects.order_by('-creation_date')
        p = Paginator(search, 1) #

        search = p.get_page(request.GET.get('page', 1)) 
       
        data = {
            'search': search,
        }
        return render(request, 'search.html', data)

class PostAdd(PermissionRequiredMixin, CreateView):

    template_name = 'add.html'
    form_class = PostForm
    permission_required = ('myapp.add_post',)

    def post(self, request, *args, **kwargs):
        #проверка на колво постов пользователя
        if self.NotAllowToPublish(request.user.id):
            return redirect('/news')

        superPost = super().post(request, *args, **kwargs) 
        categoryreq = request.POST['category']

        subscribersId = CategorySubscribers.objects.filter(category = categoryreq).values('subscribers')

        title = request.POST['post_title']
        text = request.POST['post_text']

        for userID in subscribersId:

            SubsUser = User.objects.get(id = userID['subscribers'])
            
            appointment = Appointment(
                title = title,
                text = text,
                email = SubsUser.email,
                userName = SubsUser.username,
                postUrl = superPost.url
            )
            appointment.save()
        
        return superPost

    def NotAllowToPublish(self, UserIdToCheck):
        #проверка на колво постов у пользователя
        currUser = User.objects.get(id = UserIdToCheck)
        currAuthor = Author.objects.get(author_user = currUser)
        return True if len(Post.objects.filter(creation_date__gt = date.today(), post_author = currAuthor)) >= 3 else False

class PostEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    
    model = Post
    template_name = 'edit.html'
    form_class = PostForm
    permission_required = ('myapp.change_post',)

class PostDelete(DeleteView):

    model = Post
    template_name = 'delete.html'
    success_url ="/news"