
from django.forms import ModelForm # Импортируем true-false поле
from .models import Post
 
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['post_author', 'category', 'post_choice', 'post_title', 'post_text']
