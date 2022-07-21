from django.test import TestCase

mystt = 'Титул первой новости 10 Jun 2022 Текст первой новости'

Ban_List = [
    "Новости",
    "Первой"
]

print(' '.join('*'*len(i) if i.upper() in list(map(lambda x: x.upper(), Ban_List)) else i for i in mystt.split()))
