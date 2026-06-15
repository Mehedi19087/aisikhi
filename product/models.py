from django.db import models

class Product(models.Model):
      class Status(models.TextChoices):
          DRAFT = 'draft', 'Draft'
          PUBLISHED = 'published', 'Published'
          ARCHIVED = 'archived', 'Archived'

      name = models.CharField(max_length=200)
      slug = models.SlugField(max_length=80, unique=True)
      description = models.TextField(blank=True)
      status = models.CharField(
          max_length=20,
          choices=Status.choices,
          default=Status.PUBLISHED,
      )
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

      def __str__(self):
          return self.name


class AISubscriptionPlan(models.Model):
      class AccountType(models.TextChoices):
          SHARED = 'shared', 'Shared'
          PERSONAL = 'personal', 'Personal'

      product = models.ForeignKey(
          Product,
          on_delete=models.CASCADE,
          related_name='subscription_plans',
      )
      account_type = models.CharField(
          max_length=20,
          choices=AccountType.choices,
      )
      duration_days = models.PositiveIntegerField()
      price = models.DecimalField(max_digits=10, decimal_places=2)
      title = models.CharField(max_length=200)
      features = models.TextField(blank=True)
      rules = models.TextField(blank=True)
      is_active = models.BooleanField(default=True)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

      class Meta:
          constraints = [
              models.UniqueConstraint(
                  fields=['product', 'account_type', 'duration_days'],
                  name='unique_ai_subscription_plan_option',
              )
          ]

      def __str__(self):
          return self.title
