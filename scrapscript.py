import os
import json
import subprocess
import sys

DEFAULT_NUMBER_OF_PAGES = 2
SCRAPY_CRAWL_STRING = "scrapy crawl news.ycombinator -a "
NUMBER_OF_PAGES_STRING = "no_of_pages=" + str(DEFAULT_NUMBER_OF_PAGES)
LAST_JOB_ID_STRING = "last_job_id="
LAST_JOB_ID_FILE = "job.json"


def main():
    load = load_command()
    subprocess.call(SCRAPY_CRAWL_STRING+load)


def readFile():
    try:
        with open(os.path.join(sys.path[0], LAST_JOB_ID_FILE)) as file:
            data = json.load(file)
            try:
                value = data['id']
                return value
            except Exception:
                print("LAST JOB ID NOT FOUND")
                return None
    except Exception:
        print("FILE DOES NOT EXIST")
    return None


def load_command():
    last_job_id = readFile()
    if last_job_id is None:
        return NUMBER_OF_PAGES_STRING
    else:
        return LAST_JOB_ID_STRING + str(last_job_id)


if __name__ == "__main__":
    main()
