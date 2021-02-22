from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from posts.models import Post, Group


class UrlsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='john')
        cls.user = User.objects.get(username='john')

        group = Group.objects.create(title='Тестовая группа', slug='test-group',
                                     description='тестовое описание')

        Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=group,)
        cls.post = Post.objects.get(text='Тестовый текст')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_user_two = Client()
        self.authorized_client.force_login(self.user)
        self.user_two = get_user_model().objects.create_user(username='Nagibator2007')
        self.authorized_client_user_two.force_login(self.user_two)

    def test_post_urls_guest_status(self):
        """Тестируем доступность страниц для неавторизированного поль'AnonymousUser' object is not iterableзователя."""
        post_id = self.post.id
        url_names = {
            '/': 200,
            f'/group/{Group.objects.get(id=1).slug}/': 200,
            f'/{self.user}/': 200,
            '/new/': 302,
            f'/{self.user}/{post_id}/': 200,
            f'/{self.user}/{post_id}/edit/': 302
        }
        for url, status in url_names.items():
            with self.subTest():
                response = self.guest_client.get(url).status_code
                self.assertEqual(response, status)

    def test_post_urls_authorized_status(self):
        """Тестируем доступность страниц для авторизированного пользователя."""
        post_id = self.post.id
        url_names = {
            '/': 200,
            f'/group/{Group.objects.get(id=1).slug}/': 200,
            '/new/': 200,
            f'/{self.user}/': 200,
            f'/{self.user}/{post_id}/': 200,
            f'/{self.user}/{post_id}/edit/': 200,
        }
        for url, status in url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url).status_code
                self.assertEqual(response, status)

    def test_post_urls_not_author_status(self):
        """Страница /<username>/<post_id>/edit недоступна не автору поста"""
        post_id = self.post.id
        response = self.authorized_client_user_two.get(
            f'/{self.user}/{post_id}/edit/').status_code
        self.assertEqual(response, 302)

    def test_new_post_url_redirect_anonymous_on_login(self):
        """Страница по адресу /new/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    def test_edit_url_redirect_anonymous_on_login(self):
        """Страница по адресу /<username>/<post_id>/edit/
         перенаправит анонимного пользователя на страницу регистрации."""
        post_id = self.post.id
        author = self.post.author.username
        response = self.guest_client.get(f'/{self.user}/{post_id}/edit/',
                                         follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/{author}/{post_id}/edit/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'new_post.html': '/new/',
            'group.html': f'/group/{Group.objects.get(id=1).slug}/',
            'profile.html': f'/{self.user}/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_404(self):
        """При обращение к неизвестной странице возвращается ошибка 404"""
        self.assertEqual(
            self.authorized_client.get('/noname/str/').status_code, 404)
