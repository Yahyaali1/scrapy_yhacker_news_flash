import re
import logging

from .datakeys import DataKeys


class YcombinatorParseDataPipeline(object):
    def close_spider(self, spider):
        for job in spider.items:
            self.parse_data(job)

    def parse_data(self, item):
        regex_website_split = r"(\.)"
        regex_sentence_split = r"((((i|I)s |)((h|H)(iring|ires)|((L|l)ooking)))|((w|W)ants )|((r|R)aised)|((s|S)eeking))(\s|)((a|an)|for( a|)|-|)"
        regex_company_title = r"[(]"
        regex_location = r"(in\b)"
        # Split the sentence based on given tokens
        data_sentence_split = re.split(
            regex_sentence_split, item["job_msg"], 1)

        # Is split was successful extract company name and other data
        if len(data_sentence_split) > 1:
            # Extract company data after removing brackets.
            company_name_split = re.split(
                regex_company_title, data_sentence_split[0], 1)
            item[DataKeys.COMPANY_NAME] = company_name_split[0]
            # Extract job title
            job_title_split = re.split(
                regex_location,
                data_sentence_split[len(data_sentence_split)-1], 1)

            item[DataKeys.POSITION] = job_title_split[0]

            if len(job_title_split) > 1:
                item[DataKeys.JOB_LOCATION] = job_title_split[len(
                    job_title_split)-1]
            else:
                item[DataKeys.JOB_LOCATION] = "Not Given"
        else:
            item[DataKeys.JOB_LOCATION] = "Not Given"
            if item[DataKeys.COMPANY_NAME] is not None:
                company_name_split = re.split(
                    regex_website_split, item[DataKeys.COMPANY_NAME], 1)
                item[DataKeys.COMPANY_NAME] = company_name_split[0]
            else:
                item[DataKeys.COMPANY_NAME] = "Not Given"
            item[DataKeys.JOB_TITLE] = item[DataKeys.JOB_MSG]
        logging.info("Parsed Item "+item)
