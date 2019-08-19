"""
Connects to database for storing parsed records.
Setups database connection
Contains methods for checking duplicates. 
Updates last scraped job id for future usuage
"""

import sqlite3
import logging
import json
from .datakeys import DataKeys

CREATE_TABLE_COMPANY = '''CREATE TABLE IF NOT EXISTS company (
	id integer PRIMARY KEY AUTOINCREMENT ,
	company_name text NOT NULL)'''
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
GET_COMPANY_WITH_NAME = 'SELECT id FROM company WHERE company_name=?'
GET_JOB_BY_JOB_MSG = 'SELECT job_msg FROM job WHERE job_msg=?'
INSERT_COMPANY_NAME_RECORD = 'INSERT into company (company_name) VALUES (?)'
INSERT_JOB_RECORD = 'INSERT into job (company_id,job_id,job_msg,job_location,position,job_url) VALUES (?,?,?,?,?,?)'


class YcombinatorDataBasePipeline(object):
    def __init__(self, db_name, last_job_record_file):
        self.conn = sqlite3.connect(db_name)
        self.curr = self.conn.cursor()
        self.file = last_job_record_file
        self.__setup_db()

    def __setup_db(self):
        self.curr.execute(CREATE_TABLE_COMPANY)
        self.curr.execute(CREATE_TABLE_JOB)
        self.conn.commit()

    def __commit_changes(self):
        self.conn.commit()

    def __close_connection(self):
        self.conn.close()
        pass

    @classmethod
    def from_crawler(cls, crawler):
        db_name = crawler.settings.get("SQL_DB_NAME")
        last_job_record_file = crawler.settings.get("LAST_JOB_ID_RECORD")
        return cls(db_name, last_job_record_file)

    def __company_exist(self, name: str):
        self.curr.execute(
            GET_COMPANY_WITH_NAME, (name,))
        company_id = self.curr.fetchone()
        if company_id is not None:
            return True, company_id[0]
        else:
            return False, -1

    def __job_exist(self, job_msg: str):
        self.curr.execute(GET_JOB_BY_JOB_MSG, (job_msg,))
        job_msg_db = self.curr.fetchone()
        if job_msg_db is not None:
            return True, job_msg_db
        else:
            return False, None

    def __insert_company(self, company_name: str):
        self.curr.execute(
            INSERT_COMPANY_NAME_RECORD, (company_name,))
        return self.curr.lastrowid

    def __insert_job(self, company_id: int, job_id: int, job_msg: str,
                     job_location: str, position: str, job_url: str):
        logging.info("New company created with "+str(company_id))
        self.curr.execute(
            INSERT_JOB_RECORD,
            (company_id, job_id, job_msg, job_location, position, job_url))
        return self.curr.lastrowid

    def __save_data(self, data: []):
        """
        Loops through all parsed items. 
        Insert new record for company and job posting.
        Avoids insertion if the job post is already in database.
        Returns null or latest job id that was inserted into database. 
        """
        last_job_id = None
        for job in data:
            exist, row_db = self.__job_exist(job[DataKeys.JOB_MSG])

            if exist is False:
                exist_company, company_id = self.__company_exist(
                    job[DataKeys.COMPANY_NAME])

                if exist_company:
                    self.__insert_job(
                        company_id, job[DataKeys.JOB_ID],
                        job[DataKeys.JOB_MSG],
                        job[DataKeys.JOB_LOCATION],
                        job[DataKeys.POSITION], job[DataKeys.JOB_URL])

                else:
                    company_id = self.__insert_company(
                        job[DataKeys.COMPANY_NAME])
                    self.__insert_job(
                        company_id, job[DataKeys.JOB_ID], job[DataKeys.JOB_MSG],
                        job[DataKeys.JOB_LOCATION], job[DataKeys.POSITION],
                        job[DataKeys.JOB_URL])
                last_job_id = job[DataKeys.JOB_ID]
            else:
                logging.info("Already Exist in database " +
                             job[DataKeys.JOB_MSG])

        return last_job_id

    def __update_last_job_id(self, job_id):
        if job_id is not None:
            with open(self.file, 'w') as outfile:
                json.dump({"id": job_id}, outfile)
                outfile.close()

    def close_spider(self, spider):
        self.__update_last_job_id(self.__save_data(spider.items))
        self.__commit_changes()
        self.__close_connection()
