from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Item(models.Model):
    class Status(models.TextChoices):
        LOST = "lost", "Lost"
        FOUND = "found", "Found"
        CLAIMED = "claimed", "Claimed"
        RETURNED = "returned", "Returned"
        ARCHIVED = "archived", "Archived"

    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    date_lost_or_found = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LOST)
    image = models.ImageField(upload_to='item_images', blank=True, null=True)
    reported_by = models.ForeignKey(User, related_name='reported_items', on_delete=models.CASCADE)
    claim_notes = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class ClaimRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    item = models.ForeignKey(Item, related_name="claims", on_delete=models.CASCADE)
    claimed_by = models.ForeignKey(User, related_name="item_claims", on_delete=models.CASCADE)
    note = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Claim {self.item.name} by {self.claimed_by.username} ({self.get_status_display()})"
