from django.conf.urls import url
from .views import *

urlpatterns = [
    url('search/$',Search.as_view(),name="search"),
    url('followed-users-questions/$',FollowedUsersQuestions.as_view(),name="followed_users_questions"),
    url('filter/$',Filter.as_view(),name="filter"),
    url('get-categories/$',CategoriesView.as_view(),name="categories"),
    url('other-user-fav-questions/(?P<user_id>\w+)$',OtherUserFavQuestionsView.as_view(),name="other_user_fav_questions"),
    url('other-user-questions/(?P<user_id>\w+)$',OtherUserQuestionsView.as_view(),name="other_user_questions"),
    url('my-fav-questions/$',MyFavQuestionsView.as_view(),name="fav_questions"),
    url('my-questions/$',MyQuestionsView.as_view(),name="my_questions"),
    url('question/$',Questions.as_view(),name="add_question"),
    url('upload_file_base64/$', UploadFileBase64.as_view(), name="upload_file_base64"),
    url('requert_info/$', RequertInfo.as_view(), name="requert_info"),
    url('question/(?P<id>[\w-]+)$', Questions.as_view(), name="get_delete_question"),
    url('fav-unfav/$', FavUnfavQuestion.as_view(), name="fav_unfav"),
    url('like-unlike/$', LikeUnlikeQuestion.as_view(), name="like_unlike"),
    url('notify-share/$', UserNotifyShareQuestion.as_view(), name="share"),
    url('useful-unuseful/$', UsefulUnusefulReply.as_view(), name="useful_unuseful"),
    url('report-unreport/$',ReportUnreportQuestion.as_view(),name="report_unreport"),


    ## Question-Replies APIs
    url('reply/$', Reply.as_view(), name="add_edit_reply"),
    url('reply/(?P<id>[\w-]+)/$', Reply.as_view(), name="delete_reply"),
    url('question-replies/(?P<id>[\w-]+)/$', QuestionReplies.as_view(), name="question_replies"),
    url('reply-replies/(?P<id>[\w-]+)/$', ReplyReplies.as_view(), name="question_replies"),

    url('question-replies/$', QuestionReplies.as_view(), name="question_replies"),
    url('share-question/(?P<pk>.+)/$', ShareQuestion.as_view(), name="share_question"),
]