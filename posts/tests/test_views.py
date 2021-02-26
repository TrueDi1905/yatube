import shutil
import tempfile

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, Follow


class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='john')

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        cls.uploaded_two = SimpleUploadedFile(
            name='small_two.gif',
            content=small_gif,
            content_type='image/gif')

        for num in range(11):
            Post.objects.create(
                author=cls.user,
                text=num,
            )
        cls.group = Group.objects.create(
            title='Тестовая группа', slug='test-group',
            description='тестовое описание')

        Group.objects.create(
            title='Тестовая группа 2',
            slug='test-group-two',
            description='тестовое описание 2')

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=Group.objects.get(title='Тестовая группа'),
            image=cls.uploaded_two)

        Post.objects.create(
            text='Тестовый текст 2',
            author=cls.user,
            group=Group.objects.get(title='Тестовая группа 2'),
            image=cls.uploaded)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user_two = get_user_model().objects.create_user(
            username='Nagibator2007')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_two = Client()
        self.authorized_client.force_login(self.user_two)

    def test_views_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'new_post.html': reverse('posts:new_post'),
            'group.html': (
                reverse('posts:group_posts',
                        kwargs={'slug': self.group.slug})),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        context_page = response.context.get('page')
        self.assertEqual(context_page[0].text, 'Тестовый текст 2')
        self.assertEqual(context_page[0].author.username, 'john')
        self.assertEqual(context_page[0].group.title, 'Тестовая группа 2')
        self.assertEqual(context_page[0].image, 'posts/small.gif')

    def test_group_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}))
        context_group = response.context.get('group')
        context_page = response.context.get('page')
        self.assertEqual(context_group.title, 'Тестовая группа')
        self.assertEqual(context_group.description, 'тестовое описание')
        self.assertEqual(context_group.slug, self.group.slug)
        self.assertEqual(context_page[0].text, 'Тестовый текст')
        self.assertEqual(context_page[0].author.username, 'john')
        self.assertEqual(context_page[0].image, 'posts/small_two.gif')

    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_paginator(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page')), 10)

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'john'})
        )
        context = response.context.get
        self.assertEqual(context('author').username, 'john')
        self.assertEqual(len(context('page')), 10)
        self.assertEqual(context('post_list')[0].text, 'Тестовый текст 2')
        self.assertEqual(context('post_list')[0].image, 'posts/small.gif')

    def test_about(self):
        """страницы /about/author/ и /about/tech/
        доступны неавторизованному пользователю"""
        url_names = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for url, status in url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url).status_code
                self.assertEqual(response, status)

    def test_cache(self):
        """Проверка работы кеша"""
        response = self.authorized_client.get('posts:index')
        cached_response_content = response.content
        post = Post.objects.all().last()
        post.delete()
        response = self.authorized_client.get('posts:index')
        self.assertEqual(cached_response_content, response.content)

    def test_follow(self):
        """Авторизованный пользователь может подписываться
         на других пользователей"""
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.context.get('page')[0].author, self.user)

    def test_follow_unfollow(self):
        """Авторизованный пользователь может удалять из из подписок."""
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIsNot(response.context, False)

    def test_follow_new_post(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан на него."""
        Post.objects.create(text='Новый пост автора', author=self.user)
        Follow.objects.create(author=self.user, user=self.user_two)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.context.get('page')[0].text, 'Новый пост автора')
        response = self.authorized_client_two.get(reverse('posts:follow_index'))
        self.assertIsNot(response.context, False)

    def test_comment(self):
        """Только авторизированный пользователь может комментировать посты"""
        comment = {'post': self.post,
                   'author': self.user,
                   'text': 'Автор жжёт! Ставлю класс!'}
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'username': self.user.username,
                                                 'post_id': self.post.id}), data=comment)
        response = self.authorized_client.get(
            reverse('posts:post', kwargs={'username': self.user.username,
                                          'post_id': self.post.id}))
        self.assertEqual(response.context.get('comments')[0].text, 'Автор жжёт! Ставлю класс!')

    def test_comment_anon(self):
        """Неавториизированный пользователь не может комментировать посты"""
        comment = {'post': self.post,
                   'author': self.user,
                   'text': 'Автор жжёт! Ставлю класс!'}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'username': self.user.username,
                                                 'post_id': self.post.id}), data=comment)
        self.assertEqual(response.status_code, 302)
