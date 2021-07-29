# posts/tests/tests_url.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Group


User = get_user_model()

# class StaticURLTests(TestCase):
#     def setUp(self):
#         # Устанавливаем данные для тестирования
#         # Создаём экземпляр клиента. Он неавторизован.
#         self.guest_client = Client()

#     def test_homepage(self):
#         # Отправляем запрос через client,
#         # созданный в setUp()
#         response = self.guest_client.get('/')
#         self.assertEqual(response.status_code, 200)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Group.objects.create(
            title='title',
            description='description',
            slug='test-slug'
        )

        cls.templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test-slug/',
            'new_post.html': '/new/'
        }

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_new_url_exists_at_desired_location_authorized(self):
        """Страница /new/ доступна только авторизированному пользователю"""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_url_redirect_guest(self):
        """Страница /new/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, 302)

    def test_new_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /new/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    def test_group_slug_exists_at_desired_location_authorized(self):
        """
        Страница /group/test-slug/ доступна
        авторизированному пользователю
        """
        response = self.authorized_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_group_slug_exists_at_desired_location_authorized(self):
        """
        Страница /group/test-slug/ доступна
        анонимному пользователю
        """
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """
        Шаблоны использованы верно
        """
        for template, adress in PostsURLTests.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
