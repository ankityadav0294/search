# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb


class MysqlPipeline(object):

    def open_spider(self, spider):
        self.address = 'localhost'
        self.client = 'root'
        self.password = 'vodka'
        self.database = 'crawler'
        self.connect = MySQLdb.connect(self.address, self.client, self.password, self.database)
        self.cursor = self.connect.cursor()
        for i in range(0, 1000):
            print('1')

    def close_spider(self, spider):
        self.connect.close()
        for i in range(0, 1000):
            print('3')

    def process_item(self, item, spider):
        sql = "insert into data(title, url, urlid) values ('%s','%s','%s','%s','%s')" % \
              (item['title'], item['url'], item['urlid'])

        try:
            # Execute the SQL command
            self.cursor.execute(MySQLdb.escape_string(sql))
            # Commit your changes in the database
            self.connect.commit()
        except:
            # Rollback in case there is any error
            self.connect.rollback()

        for i in range(0, 1000):
            print('2')
        return item

