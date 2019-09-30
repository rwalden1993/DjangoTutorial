from django.urls import re_path

from gameplay.views import game_detail, make_move

urlpatterns = [
    re_path(r'detail/(?P<id>\d+)/$',
            game_detail,
            name='gameplay_detail'),
    re_path(r'make_move/(?P<id>\d+)/',
            make_move,
            name='gameplay_make_move')
]