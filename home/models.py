from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel

class HomePage(Page):
    body = StreamField([
        ('hero', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('subtitle', blocks.TextBlock()),
            ('cta_text', blocks.CharBlock()),
            ('cta_link', blocks.URLBlock()),
        ])),
        ('cards', blocks.ListBlock(blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('description', blocks.TextBlock()),
            ('icon', blocks.CharBlock(help_text="Bootstrap icon name")),
        ]))),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
