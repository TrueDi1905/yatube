import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from posts.forms import PostForm
from posts.models import Post, Group


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create_user(username='john')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='тестовое описание')

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group, )
        cls.form = PostForm

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Просто текст',
            'group': PostCreateFormTests.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(group=PostCreateFormTests.group.id).exists())
        self.assertEqual(
            Post.objects.filter(
                group=PostCreateFormTests.group.id).first().text, 'Просто текст')
        self.assertEqual(
            Post.objects.filter(
                group=PostCreateFormTests.group.id).first().author.username, 'john')
        self.assertEqual(
            Post.objects.filter(
                group=PostCreateFormTests.post.id).first().image, 'posts/small.gif')

    def test_edit_post(self):
        """При редактировании поста, изменяется запись в базе данных."""
        form_data = {
            'text': 'Новый текст',
            'group': PostCreateFormTests.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=[self.user.username, self.post.id]),
            data=form_data)
        self.assertEqual(
            Post.objects.filter(id=self.post.id).last().text, 'Новый текст')
