# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from random import randint
from datetime import datetime, timedelta
import logging

from amundsen_application.models.announcements import Announcements, Post
from amundsen_application.base.base_announcement_client import BaseAnnouncementClient
from neo4j import GraphDatabase


class Neo4jConnection:
      def __init__(self, uri, user, pwd):
          self.__uri = uri
          self.__user = user
          self.__pwd = pwd
          self.__driver = None
          try:
              self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd), encrypted=False)
          except Exception as e:
              logging.error("Failed to create the driver: " + str(e))
             
      def close(self):
          if self.__driver is not None:
              self.__driver.close()

      def query(self, query, db=None):
          assert self.__driver is not None, "Driver not initialized!"
          session = None
          response = None
          try:
              session = self.__driver.session(database=db) if db is not None else self.__driver.session()
              response = list(session.run(query))
          except Exception as e:
              print("Query failed:", e)
          finally:
              if session is not None:
                  session.close()
          return response


class Neo4jAnnouncementClient(BaseAnnouncementClient):
    def __init__(self) -> None:
        pass

    
    def get_posts(self) -> Announcements:
        """
        Returns an instance of amundsen_application.models.announcements.Announcements, which should match
        amundsen_application.models.announcements.AnnouncementsSchema
        """
        conn = Neo4jConnection(uri="bolt://192.168.137.227:7687", user="neo4j", pwd="test")
        query = """
            MATCH (n:Announcement) 
            RETURN n as announcements
            ORDER BY n.createdAt DESC
            LIMIT 10
        """

        results = conn.query(query)

        announcements_nodes = [i['announcements'] for i in results]
        announcements = []
        for announcement in announcements_nodes:
            announcements.append(announcement._properties)
        posts = []
        
        for row in announcements:
            post = Post(title=row['title'],
                        date=datetime(row['createdAt'].year, row['createdAt'].month, row['createdAt'].day, row['createdAt'].hour, row['createdAt'].minute, int(row['createdAt'].second)).strftime('%b %d %Y %H:%M:%S'),
                        html_content=row['description'])
            posts.append(post)

        return Announcements(posts)
