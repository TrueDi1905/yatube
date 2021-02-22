from django.test import TestCase
from django.contrib.auth.models import User

from posts.models import Post, Group


class PostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username='john')

        group = Group.objects.create(title='Тестовая группа', slug='test-group',
                                     description='тестовое описание')

        Post.objects.create(
            text='Тестовый текст',
            author=user,
            group=group,)
        cls.post = Post.objects.get(text='Тестовый текст')

    def test_verbose(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostTest.post
        field_verbose = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostTest.post
        field_verbose = {
            'text': 'Напишите содержимое поста',
            'group': 'Укажите название группы',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_str_post(self):
        """метод __str__ в классе Post совпадает с ожидаемым."""
        post = PostTest.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))

    def test_str_group(self):
        """метод __str__ в классе Group совпадает с ожидаемым."""
        group = PostTest.post.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
