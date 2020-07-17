from django.conf.urls import url
from .views import *

urlpatterns = [
    url('get-posts/$', PostsView.as_view(), name="get_posts"),
    url('system-updates/(?P<posts_timestamp>\d+\.\d+)/(?P<followers_questions_timestamp>\d+\.\d+)/(?P<notifications_timestamp>\d+\.\d+)/$',
        PostsHaveUpdatesView.as_view(), name="posts_have_updates"),
    url('get-rev-setting/$', GetRevSettingView.as_view(), name="get_rev_setting"),
    url('get-channel-posts/$', ChannelPostsView.as_view(), name="get_channel_posts"),
    url('like-unlike/$', LikeUnlikePost.as_view(), name="like_unlike"),
    url('share-post/(?P<pk>.+)/$', SharePost.as_view(), name="share_post"),
    url('media-post/(?P<pk>.+)/$', MediaPost.as_view(), name="show_post_media"),
]