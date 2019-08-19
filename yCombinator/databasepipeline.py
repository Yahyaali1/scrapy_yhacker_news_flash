# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
import json
from .datakeys import DataKeys

CREATE_TABLE_COMPANY = '''CREATE TABLE IF NOT EXISTS company (
	id integer PRIMARY KEY AUTOINCREMENT ,
	company_name text NOT NULL
)'''
CREATE_TABLE_JOB = '''CREATE TABLE IF NOT EXISTS job (
	id integer PRIMARY KEY AUTOINCREMENT ,
  	company_id Integer,
	job_id Integer,
  	job_msg Text,
  	job_location Text,
  	position Text,
    job_url Text,
  	time_stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  	FOREIGN KEY(company_id) REFERENCES company(id)
)'''


class YcombinatorDataBasePipeline(object):
    def __init__(self, db_name, last_job_record_file):
        self.conn = sqlite3.connect(db_name)
        self.curr = self.conn.cursor()
        self.file = last_job_record_file
        self.setup_db()

    def setup_db(self):
        self.curr.execute(CREATE_TABLE_COMPANY)
        self.curr.execute(CREATE_TABLE_JOB)
        self.conn.commit()

    def commit_changes(self):
        self.conn.commit()

    def close_connection(self):
        self.conn.close()
        pass

    @classmethod
    def from_crawler(cls, crawler):
        db_name = crawler.settings.get("SQL_DB_NAME")
        last_job_record_file = crawler.settings.get("LAST_JOB_ID_RECORD")
        return cls(db_name, last_job_record_file)

    def company_exist(self, name: str):
        self.curr.execute(
            'SELECT id FROM company WHERE company_name=?', (name,))
        company_id = self.curr.fetchone()
        if company_id is not None:
            return True, company_id[0]
        else:
            return False, -1

    def job_exist(self, job_msg: str):
        self.curr.execute(
            'SELECT job_msg FROM job WHERE job_msg=?', (job_msg,))
        job_msg_db = self.curr.fetchone()
        if job_msg_db is not None:
            return True, job_msg_db
        else:
            return False, None

    def insert_company(self, company_name: str):
        self.curr.execute(
            'INSERT into company (company_name) VALUES (?)', (company_name,))
        return self.curr.lastrowid

    def insert_job(self, company_id: int, job_id: int, job_msg: str,
                   job_location: str, position: str, job_url: str):
        print(company_id)
        self.curr.execute(
            'INSERT into job (company_id,job_id,job_msg,job_location,position,job_url) VALUES (?,?,?,?,?,?)',
            (company_id, job_id, job_msg, job_location, position, job_url))
        return self.curr.lastrowid

    def save_data(self, data: []):
        last_job_id = None
        for job in data:
            exist, row_db = self.job_exist(job[DataKeys.JOB_MSG])

            if exist is False:
                exist_company, company_id = self.company_exist(
                    job[DataKeys.COMPANY_NAME])
                print(company_id)

                if exist_company:
                    self.insert_job(
                        company_id, job[DataKeys.JOB_ID],
                        job[DataKeys.JOB_MSG],
                        job[DataKeys.JOB_LOCATION],
                        job[DataKeys.POSITION], job[DataKeys.JOB_URL])

                else:
                    company_id = self.insert_company(
                        job[DataKeys.COMPANY_NAME])
                    self.insert_job(
                        company_id, job[DataKeys.JOB_ID], job[DataKeys.JOB_MSG],
                        job[DataKeys.JOB_LOCATION], job[DataKeys.POSITION],
                        job[DataKeys.JOB_URL])
                last_job_id = job[DataKeys.JOB_ID]
            else:
                print("Already Exist"+job[DataKeys.JOB_MSG])

        return last_job_id

    def update_last_job_id(self, job_id):
        if job_id is not None:
            with open(self.file, 'w') as outfile:
                json.dump({"id": job_id}, outfile)
                outfile.close()

    def close_spider(self, spider):
        self.update_last_job_id(self.save_data(spider.items))
        self.commit_changes()
        self.close_connection()
