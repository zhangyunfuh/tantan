"""swiper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from user import api
from social import api as social_api

urlpatterns = [
    url(r'^api/user/submit/phone/$', api.submit_phone),
    url(r'^api/user/submit/vcode/$', api.submit_vcode),
    url(r'^api/user/get/profile/$', api.get_profile),
    url(r'^api/user/edit/profile/$', api.edit_profile),
    url(r'^api/user/upload/avatar/$', api.upload_avatar),

    url(r'^api/social/rcmd/list/$', social_api.get_rcmd_list),
    url(r'^api/social/like/$', social_api.like),
    url(r'^api/social/superlike/$', social_api.superlike),
    url(r'^api/social/dislike/$', social_api.dislike),
    url(r'^api/social/rewind/$', social_api.rewind),
    url(r'^api/social/show/like/me/$', social_api.get_liked_list),

    url(r'^api/social/friends/$', social_api.friends),

    url(r'^api/social/hot/users/$', social_api.hot_users),

]
