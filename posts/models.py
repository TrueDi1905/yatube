from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст', help_text='Напишите содержимое поста')
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts", verbose_name='Автор')
    group = models.ForeignKey('Group', on_delete=models.CASCADE,
                              related_name="posts", blank=True, null=True,
                              verbose_name='Группа', help_text='Укажите название группы')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.fields.SlugField(unique=True, verbose_name="Уникальный адрес")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE,
                             related_name="comments", verbose_name='Комментарий')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Автор")
    text = models.TextField(verbose_name='Текст',
                            help_text='Оставьте комментарий')
    created = models.DateTimeField("date published", auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
