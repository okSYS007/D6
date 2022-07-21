from django import template
 
register = template.Library()

@register.filter(name='Censor')  
def Censor(value, arg):

    Ban_List = [    
        "Новости",
        "lorem",
        "ipsum"
    ]
   
    return ' '.join('*'*len(i) if i.upper() in list(map(lambda x: x.upper(), Ban_List)) else i for i in value.split())