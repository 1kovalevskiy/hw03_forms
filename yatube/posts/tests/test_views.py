from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.paginator import Paginator


from posts.models import Group, Post

User = get_user_model()


class PostPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='title',
            description='description',
            slug='test-slug'
        )
        cls.group2 = Group.objects.create(
            title='title2',
            description='description2',
            slug='test-slug2'
        )
        cls.user = User.objects.create_user(username='TestUser')
        for i in range(13):
            Post.objects.create(
                text=f'text{i}',
                author=PostPageTests.user,
                group=PostPageTests.group,
            )

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPageTests.user)
    
    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            'index.html': reverse('index'),
            'new_post.html': reverse('new_post'),
            'group.html': reverse('group_posts', args=[PostPageTests.group.slug]),
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.       
        self.assertEqual(len(response.context['page']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.guest_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context['page']), 3) 

    def test_new_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)


    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        self.assertEqual(task_text_0, 'text12')
        self.assertEqual(task_author_0, PostPageTests.user)
        self.assertEqual(task_group_0, PostPageTests.group)
    
    def test_grop_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('group_posts',
                                    args=[PostPageTests.group.slug]))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        self.assertEqual(task_text_0, 'text12')
        self.assertEqual(task_author_0, PostPageTests.user)
        self.assertEqual(task_group_0, PostPageTests.group)

    def test_group2_is_empty(self):
        """Запись не отображается в группе 2"""
        response = self.authorized_client.get(reverse('group_posts',
                                    args=[PostPageTests.group2.slug]))
        objects = response.context['page']
        self.assertEqual(len(objects), 0)
