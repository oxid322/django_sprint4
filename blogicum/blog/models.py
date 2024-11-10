from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import ImageField
from django.urls import reverse

User = get_user_model()


class Location(models.Model):
    name = models.CharField('Название места', max_length=256)
    is_published = models.BooleanField('Опубликовано',
                                       default=True)
    created_at = models.DateTimeField('Добавлено',
                                      auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Category(models.Model):
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField('Идентификатор',
                            unique=True,
                            help_text='Идентификатор страницы для URL;'
                                      ' разрешены символы латиницы,'
                                      ' цифры, дефис и подчёркивание.')
    is_published = models.BooleanField('Опубликовано',
                                       default=True,
                                       help_text='Снимите галочку, '
                                                 'чтобы скрыть публикацию.')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Post(models.Model):
    title = models.CharField('Заголовок',
                             max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата и время публикации',
                                    help_text='Если установить дату и время'
                                              ' в будущем — можно'
                                              ' делать отложенные публикации.')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации',
                               related_name='author')
    location = models.ForeignKey(Location,
                                 on_delete=models.SET_NULL,
                                 blank=True,
                                 verbose_name='Местоположение',
                                 null=True,
                                 related_name='location')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 verbose_name='Категория',
                                 null=True,
                                 related_name='category')
    is_published = models.BooleanField('Опубликовано',
                                       default=True,
                                       help_text='Снимите галочку,'
                                                 ' чтобы скрыть публикацию.')
    created_at = models.DateTimeField('Добавлено',
                                      auto_now_add=True)
    image = ImageField(upload_to='blog/%Y/%m/%d',
                       null=True,
                       blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']
        indexes = [models.Index(fields=['-pub_date'])]


class Comment(models.Model):
    author = models.ForeignKey(User,
                               related_name='comments',
                               on_delete=models.CASCADE)
    post = models.ForeignKey(Post,
                             related_name='comments',
                             on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
