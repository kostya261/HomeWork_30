from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from lms.models import Curse, Lesson
from lms.serializers import CurseSerializer, LessonSerializer, CurseDetailSerializer
from users.permissions import IsModer, IsOwner, NotModer


class CurseViewSet(viewsets.ModelViewSet):
    serializer_class = CurseSerializer
    queryset = Curse.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CurseDetailSerializer
        return CurseSerializer

    def perform_create(self, serializer):
        """Автоматически назначаем владельца"""
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, NotModer]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, NotModer, IsOwner]
        else:  # list, retrieve
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [NotModer, IsAuthenticated]

    def perform_create(self, serializer):
        """Автоматически назначаем владельца"""
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModer | IsOwner, IsAuthenticated]


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModer | IsOwner, IsAuthenticated]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, NotModer, IsOwner]
