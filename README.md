# scrapy_yhacker_news_flash

## Project Approach 
- Scrapes Job Posting from [Hacker News](https://news.ycombinator.com/jobs?)
- Can be scheduled using the instructions listed below. (for linux you would need to start cron job)
- Uses sqlite for storing scrapped job listing
- Uses "job id" to limit number of job listing scrapped after first cycle
### How to instructions:
#### Run Scraper
- Clone/extract project files in your local drive 
- Create virtual enviornment under your project dir
- To install project dependencies run 
  `` pip -r install requirements.txt``
#### Change default pages scraped
- Open "scrapscript.py"
- Change the value for variable ``DEFAULT_NUMBER_OF_PAGES = 2``

#### You will need following things to schedule a job on windows:
- Path to python.exe:  <br />
  Run following script in your cmd if you are not aware of the location for python.exe <br />
  `python -c "import sys; print(sys.executable)"` <br />
- Path to "scrapscript.py" after extraction of project files <br />
- Open task scheduler on windows
- Under actions tab click "create task". Create task window will pop up.
- Navigate to action tab on create task window. 
- Fill in your path to python.exe and "scrapscript.py" under "Program/script" and "Start in" fields respectively.  
- Under "Add Arguments" enter "scrapscript.py"
- Navigate to Triggers tab. Click on Add. Configure the timing for your script to run as per your need. 
- Fill in details such as "task name" under general tab. 
- Clicking "Ok" on this window will save the task for you. After you have saved the task you need to select the task and run it. 


