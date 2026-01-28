from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Section, Category, Topic, Post, FreelanceJob, JobReview, DailyTip, QuizQuestion, QuizScore, SuccessStory, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['avatar', 'rank', 'title', 'reputation']

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile']

    def get_profile(self, obj):
        try:
            return ProfileSerializer(obj.profile).data
        except Exception:
            return None

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'icon_class', 'description']

class SectionSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    class Meta:
        model = Section
        fields = ['id', 'title', 'categories']

class TopicSerializer(serializers.ModelSerializer):
    starter = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ['id', 'subject', 'starter', 'category', 'views', 'created_at', 'replies_count', 'is_pinned', 'is_closed']

    def get_replies_count(self, obj):
        return getattr(obj, 'replies_count', 0)

class PostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'message', 'created_by', 'topic', 'created_at', 'likes', 'is_best_answer']

class JobReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    class Meta:
        model = JobReview
        fields = ['id', 'reviewer', 'rating', 'comment', 'created_at']

class FreelanceJobSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = FreelanceJob
        fields = ['id', 'title', 'budget_min', 'budget_max', 'owner', 'category', 'created_at', 'is_featured']

class DailyTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyTip
        fields = ['id', 'content']

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'category', 'difficulty']

class QuizScoreSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = QuizScore
        fields = ['user', 'correct_answers', 'total_points']

class SuccessStorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = SuccessStory
        fields = ['id', 'user', 'quote', 'achievements', 'resources']

class HomeDataSerializer(serializers.Serializer):
    """Anasayfa için toplu veri yapısı"""
    total_topics = serializers.IntegerField()
    total_posts = serializers.IntegerField()
    total_users = serializers.IntegerField()
    completed_jobs = serializers.IntegerField()
    # Diğer karmaşık alanlar view içinde manuel eklenecek veya buraya nested serializer olarak tanımlanabilir