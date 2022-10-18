
import os
import contentful
from rich_text_renderer import RichTextRenderer

from random import randint
from datetime import datetime, timedelta

from amundsen_application.models.announcements import Announcements, Post
from amundsen_application.base.base_announcement_client import BaseAnnouncementClient

class ContentfulAnnouncementClient(BaseAnnouncementClient):
    def __init__(self) -> None:
        self.cat = os.getenv("ANNOUNCEMENT_CLIENT_CONTENTFUL_CATEGORY", "")
        self.content_type = os.getenv("ANNOUNCEMENT_CLIENT_CONTENTFUL_CONTENT_TYPE", "announcement")
        self.client = contentful.Client(
          os.getenv("ANNOUNCEMENT_CLIENT_CONTENTFUL_SPACE"),
          os.getenv("ANNOUNCEMENT_CLIENT_CONTENTFUL_TOKEN")
        )
        self.renderer = RichTextRenderer()

    def get_posts(self) -> Announcements:
        entries = self.client.entries({'content_type': self.content_type, 'fields.category': self.cat})

        """
        Returns an instance of amundsen_application.models.announcements.Announcements, which should match
        amundsen_application.models.announcements.AnnouncementsSchema
        """
        posts = []

        for row in entries:
            post = Post(title=row.title,
                        date=row.date.strftime('%b %d %Y %H:%M:%S'),
                        html_content=self.renderer.render(row.content))
            posts.append(post)

        return Announcements(posts)