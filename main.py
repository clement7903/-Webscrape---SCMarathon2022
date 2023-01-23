from bs4 import BeautifulSoup
import csv
import requests as req
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from os.path import exists

disable_warnings(InsecureRequestWarning)

OUTPUT_FILENAME = 'full_marathon_all_2nd_half_timing.csv'
# current_link = 'https://www.sportsplits.com/races/singapore-marathon-2022/events/1/' # full marathon - all
# current_link = 'https://www.sportsplits.com/races/singapore-marathon-2022/events/1/results/custom/3/' # full marathon - SGreans only
# current_link = 'https://www.sportsplits.com/races/singapore-marathon-2022/events/1/results/custom/1/' # full marathon - all 1st half timing
# current_link = 'https://www.sportsplits.com/races/singapore-marathon-2022/events/1/results/custom/2/' # full marathon - all 2nd half timing 
# current_link = 'https://www.sportsplits.com/races/singapore-marathon-2022/events/3/' # half marathon - all

# 1. Find the table class
def find_table_class(soup):
  text_table=soup.find("table",{"class":"table table-striped u-table--v1 mb-0"})
  return text_table
  
# 2. Find the table headings
def find_table_headings(text_table):
  table_heading = text_table.thead.find_all('th')
  t_headers = []
  for t_header in table_heading:
    if t_header.text:               # if not empty
      t_headers.append(t_header.text)
  return t_headers

# 3. Find the table rows + add to page_data
def return_page_data(text_table):
  t_rows = text_table.tbody.find_all('tr')
  page_data = []

  for tr in t_rows:
    t_row = {}
    for td, th in zip(tr.find_all("td"), find_table_headings(find_table_class(soup))): # match each table row data to table header
      t_row[th] = td.text.replace('\n', '').replace('\t', '').replace('\xa0', ' ').replace('|', '').strip()

    page_data.append(t_row)
  return page_data

def append_to_existing_csv():
  with open(OUTPUT_FILENAME, 'a', newline='',encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, table_headings)
        for person in page_data:
          if person:
            writer.writerow(person)

def write_new_csv():
  with open(OUTPUT_FILENAME, 'w', newline='',encoding="utf-8") as out_file:
      writer = csv.DictWriter(out_file, table_headings)
      writer.writeheader()
      for person in page_data:
        if person:
          writer.writerow(person)

counter = 0
while True:
  r = req.get(current_link, verify=False)
  soup = BeautifulSoup(r.content, "html.parser")

  # Steps 1-3 are in table.py

  # 4. Use the functions above to extract needed data
  table = find_table_class(soup)
  table_headings = find_table_headings(table)
  page_data = return_page_data(table)  # list of dictionaries, where each dictionary is a person e.g. {'Pos': '101', 'Name': 'KEVIN HII (#1678)', ... ,'Net Pos': '103'}

  # 5a. If csv file exists, append rows only
  if exists(OUTPUT_FILENAME):
    append_to_existing_csv()
    
  # 5b. If csv doesn't exist, write new csv file
  else:
    write_new_csv()
    
  # 6. Iterates to the next page, repeats the extraction
  next_button = soup.find("a",{"class":"page-link", "rel" : "next"})
  next_link = next_button.get('href')

  current_link = next_link
  counter += 1
  print('Now at this link:', next_link)