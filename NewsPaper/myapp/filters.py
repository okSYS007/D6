from django_filters import FilterSet
from .models import Post
 
class PostFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'category': ['exact'],
            'creation_date':['gt'], 
            'post_author':['exact'],
        }