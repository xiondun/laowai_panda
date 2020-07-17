from rest_framework import serializers
from accounts.serializers import BasicUserInfoSerializer
from .models import *
from generic_relations.relations import GenericRelatedField
from connect.serializers import QuestionSerializer, QuestionReplySerializer
from connect.models import Question, QuestionReply
from accounts.models import User
from accounts.serializers import BasicUserInfoSerializer
import json


class NotificationSerializer(serializers.ModelSerializer):
    from_user = BasicUserInfoSerializer()
    to_user = BasicUserInfoSerializer()
    timestamp = serializers.SerializerMethodField()
    notification_object = GenericRelatedField(
        {
            Question: QuestionSerializer(),
            QuestionReply: QuestionReplySerializer(),
            User: BasicUserInfoSerializer(),
        }
    )
    action = serializers.SerializerMethodField()
    extra_data = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notification_object'].context.update(self.context)

    class Meta:
        model = Notification
        fields = ('id', 'from_user', 'to_user', 'notification_object', 'timestamp',
                  'created', 'title', 'message', 'action', 'seen', 'content_type', 'extra_data')

    def get_action(self, obj):
        return str(dict(NotificationTemplate.ACTION_CHOICES)[obj.action])

    def get_timestamp(self, obj):
        return obj.modified.timestamp()

    def get_extra_data(self, obj):
        if obj.extra_data:
            return json.loads(obj.extra_data)
        else:
            return

    def get_content_type(self, obj):
        return obj.content_type.model
