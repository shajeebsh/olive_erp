from django.db import models
from finance.models import JournalEntryLine

class RelatedPartyTransaction(models.Model):
    RELATIONSHIP_CHOICES = [
        ('subsidiary', 'Subsidiary'),
        ('associate', 'Associate'),
        ('joint_venture', 'Joint Venture'),
        ('director_related', 'Director Related'),
        ('key_management', 'Key Management Personnel'),
        ('other', 'Other Related Party'),
    ]
    
    journal_entry_line = models.OneToOneField(JournalEntryLine, on_delete=models.CASCADE, related_name='related_party_detail')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.journal_entry_line.id} - {self.relationship_type}"
