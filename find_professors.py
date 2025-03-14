import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

def find_professors():
    search_file = Path.cwd() / 'html' / 'SETS_instructors.htm'
    with open(search_file, 'r') as f:
        html_content = f.read()

    doc = BeautifulSoup(html_content, 'html.parser')

    s = doc.find('select', id = "ContentPlaceHolder1_EvalsContentPlaceHolder_ddlInstructor")

    option_divs = s.find_all('option')[1:]
    instructors = []
    for option in option_divs:
        instructors.append({"name": option.text.rstrip(), "pid": option['value']})
    json_file = Path.cwd() / 'json' / 'instructors.json'
    with open(json_file, 'w') as f:
        json.dump(instructors, f)
    return instructors

find_professors()