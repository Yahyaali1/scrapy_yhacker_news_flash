import os
import json
import subprocess
import sys
import logging

DEFAULT_NUMBER_OF_PAGES = 2
SCRAPY_CRAWL_STRING = "scrapy crawl news.ycombinator -a "
NUMBER_OF_PAGES_STRING = "no_of_pages=" + str(DEFAULT_NUMBER_OF_PAGES)
LAST_JOB_ID_STRING = "last_job_id="
LAST_JOB_ID_FILE = "job.json"


def main():
    load = load_command()
    subprocess.call(SCRAPY_CRAWL_STRING+load)


def readFile():
    """
    Reads the job id of last job post that was scrapped
    """
    try:
        print(os.path.join(sys.path[0], LAST_JOB_ID_FILE))
        with open(os.path.join(sys.path[0], LAST_JOB_ID_FILE)) as file:
            data = json.load(file)
            try:
                value = data['id']
                return value
            except Exception:
                logging.warning("LAST JOB ID NOT FOUND")
                return None
    except Exception:
        logging.warning(
            "FILE DOES NOT EXIST WILL BE CREATED AT THE END OF FIRST CYCLE")
    return None


def load_command():
    """
    Loads respective command based on the last job id or number of pages to scrap
    """
    last_job_id = readFile()
    if last_job_id is None:
        return NUMBER_OF_PAGES_STRING
    else:
        return LAST_JOB_ID_STRING + str(last_job_id)


if __name__ == "__main__":
    main()
