# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from selenium.webdriver.common.devtools.v85.media import Timestamp


class LinkedInScraperPipeline:
    def open_spider(self, spider):
        # Open database connection
        self.conn = psycopg2.connect(
            dbname='Crawler',
            user='postgres',
            password='123',
            host='localhost'
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        # Close the database connection
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        # Insert scraped data into the database
        self.cursor.execute("""
            INSERT INTO posts (user_id, content, post_url)
            VALUES (
                (SELECT user_id FROM users WHERE name = %s),
                %s, %s
            );
        """, (item['owner_name'], item['content'], ""))

        # If the owner is not already in the database, insert it into the 'users' table
        self.cursor.execute("""
            INSERT INTO users (name)
            SELECT %s WHERE NOT EXISTS (SELECT 1 FROM users WHERE name = %s);
        """, (item['owner_name'], item['owner_name']))

        return item



