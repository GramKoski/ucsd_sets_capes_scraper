"""
####################
IMPORTANT: The external files that I query from and write to such as any html, json, or list of professors
is sensitive information and thus will not be added to the github. In general you must need valid UC San Diego authentication
information to use this project. You must set up and save the necessary files manually to get started scraping. If you have any 
question please contact me.
####################
"""

import requests
import os
from pathlib import Path
from http.cookiejar import Cookie, LWPCookieJar
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
from find_professors import find_professors
from parse import parse_sets_data, parse_capes_data
import time

# Find the json directory
json_dir = Path.cwd() / 'json'
html_dir = Path.cwd() / 'html'

json_dir.mkdir(exist_ok=True)
html_dir.mkdir(exist_ok = True)

print(f"Saving files to: {json_dir.absolute()}")

# Create a session
session = requests.Session()

# New function to load cookies from JSON
def load_cookies_from_json(json_file):
    try:
        with open(json_file, 'r') as f:
            cookies_json = json.load(f)
        
        # Iterate through each cookie in the JSON
        for cookie in cookies_json:
            # Create a cookie object and add it to the session
            session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                path=cookie['path'],
                secure=cookie['secure'],
                expires=cookie.get('expirationDate')
            )
        print(f"Loaded {len(cookies_json)} cookies from JSON file")
        return True
    except Exception as e:
        print(f"Error loading cookies from JSON: {e}")
        return False

# Update the cookie loading part in your script
cookie_file = json_dir / 'cookies.json'
if cookie_file.exists():
    load_cookies_from_json(cookie_file)
    print("Loaded cookies from JSON file")
else:
    print("Cookie file not found, trying manual cookie approach")
    def create_cookie(name, value, domain, path, secure=False, expires=None):
        return Cookie(
            version=0, 
            name=name, 
            value=value,
            port=None, 
            port_specified=False,
            domain=domain,
            domain_specified=True,
            domain_initial_dot=domain.startswith('.'),
            path=path, 
            path_specified=True,
            secure=secure, 
            expires=expires if expires else None, 
            discard=expires is None,
            comment=None, 
            comment_url=None, 
            rest={'HttpOnly': None},
            rfc2109=False
        )

    # Cookie jar for manual cookies
    cookie_jar = LWPCookieJar()
    session.cookies = cookie_jar

    # Focus on authentication-related cookies
    cookies_data = [
        # Make sure these are all CURRENT cookies from your authenticated browser session
        {"name": "ASP.NET_SessionId", "value": "put value here", "domain": "academicaffairs.ucsd.edu", "path": "/", "secure": True},
        {"name": "_saml_idp", "value": "put value here", "domain": "academicaffairs.ucsd.edu", "path": "/", "secure": True},
        {"name": "_shibsession_ domain id goes here", "value": "value goes here", "domain": "academicaffairs.ucsd.edu", "path": "/", "secure": True},
        {"name": "svcaaLogin", "value": "4A67... value goes here", "domain": "academicaffairs.ucsd.edu", "path": "/", "secure": True},
    ]

    for cookie_data in cookies_data:
        cookie = create_cookie(**cookie_data)
        cookie_jar.set_cookie(cookie)

# Update user agent to match the browser you are using. Scraper was developed with chrome
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://academicaffairs.ucsd.edu/Modules/Evals/SET/Reports/Search.aspx',
    'Cache-Control': 'max-age=0'
}

# Target URL
url = "https://academicaffairs.ucsd.edu/Modules/Evals/SET/Reports/Search.aspx"

def find_prof(professor_name, professor_pid):
    try:
        
        # First, get the page to grab fresh form values
        print("Accessing search page to get form values...")
        response = session.get(url, headers=headers, allow_redirects=True)
        
        # Save the initial response for debugging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = html_dir / "search_page.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Check if we got redirected to a login page
        if "login" in response.url.lower() or "duo" in response.url.lower():
            print(f"Redirected to login: {response.url}")
            print("Your session cookies are invalid or expired. Please get fresh cookies.")
            return
            
        # Parse the response to get the form values
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the form values - find the actual input elements
        try:
            viewstate = soup.select_one('input[name="__VIEWSTATE"]')['value']
            viewstategenerator = soup.select_one('input[name="__VIEWSTATEGENERATOR"]')['value']
            event_validation = soup.select_one('input[name="__EVENTVALIDATION"]')['value'] if soup.select_one('input[name="__EVENTVALIDATION"]') else ""
            
            print("Successfully extracted form values:")
            print(f"VIEWSTATE: {viewstate[:20]}...")
            print(f"VIEWSTATEGENERATOR: {viewstategenerator}")
        except (TypeError, KeyError) as e:
            print(f"Error extracting form values: {e}")
            print("Page might not have loaded properly or authentication failed")
            return
        
        # Create form submission with extracted values
        form_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
        }
        
        # Add event validation if present
        if event_validation:
            form_data['__EVENTVALIDATION'] = event_validation
            
        # Add the form fields for searching
        form_data.update({
            'ctl00$ctl00$ContentPlaceHolder1$EvalsContentPlaceHolder$ddlUnit': '',
            'ctl00$ctl00$ContentPlaceHolder1$EvalsContentPlaceHolder$cddUnit_ClientState': ':::',
            'ctl00$ctl00$ContentPlaceHolder1$EvalsContentPlaceHolder$CascadingDropDown4_ClientState': ':::',
            'ctl00$ctl00$ContentPlaceHolder1$EvalsContentPlaceHolder$ddlInstructor': str(professor_pid),
            'ctl00$ctl00$ContentPlaceHolder1$EvalsContentPlaceHolder$btnSubmit': 'Search',
            'hiddenInputToUpdateATBuffer_CommonToolkitScripts': '0'
        })
        
        print(f"Submitting search for {professor_name}")
        search_response = session.post(url, data=form_data, headers=headers, allow_redirects=True)
        
        # Check if we got redirected to login
        if "login" in search_response.url.lower() or "duo" in search_response.url.lower():
            print(f"POST request redirected to login: {search_response.url}")
            print("Your session cookies are invalid or expired. Please get fresh cookies.")
            return
            
        # Save the search response
        search_file = html_dir / "search_results.html"
        with open(search_file, "w", encoding="utf-8") as f:
            f.write(search_response.text)
        
            
        print(f"Search results saved to: {search_file}")
        
        # Check if search was successful by looking for indicators in the content
        if "No results found" in search_response.text:
            print("Search completed but no results were found.")
        elif any(term in search_response.text for term in ["student evaluation", "CAPE", "instructor", "course"]):
            print("Search successful - results found")
            return BeautifulSoup(search_response.text, 'html.parser')
        else:
            print("Search completed but response doesn't contain expected content")
        
            
    except Exception as e:
        print(f"Error accessing page: {e}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = html_dir / f"error_{timestamp}.txt"
        with open(error_file, "w", encoding="utf-8") as f:
            f.write(f"Error occurred at {datetime.now().isoformat()}\n")
            f.write(f"Error message: {str(e)}\n")
        print(f"Error information saved to: {error_file}")

# Getting index of professor from list in lexographical order. Useful for distributing the scraping process.
def get_index(professor_name, instructors):
    for i in range(len(instructors)):
        if (instructors[i]['name'] == professor_name):
            return i
    return -1


def main():
    # Add which professor you would like to start with. The scrape works in lexigraphical order of professor names.
    start_prof = "Aamari, Eddie"
    instructor_file = json_dir / 'instructors.json'

    # Note again these are hidden files for data privacy. Not available to github users. You can set up the instructors list json file 
    # by going to (and reading the comments) of the find_professors.py file
    with open(instructor_file, 'r') as f:
        content = f.read()
    
    # Loading the list of instructors for indexing
    instructors = json.loads(content)

    start = get_index(start_prof, instructors)
    end = len(instructors)-1;

    # Again, result file is hidden for data privacy. 
    result_file = json_dir / f"results{start}-{end}.json"
    all_profs = []

    # Main scraping for loop. Note that the results file is open and closed each time. This slows down the scrape, but
    # means that the result will be saved in the case of an error that breaks the loop.
    for i in range(start, end+1):
        prof = instructors[i]
        soup = find_prof(prof['name'], prof['pid'])
        search_res = parse_sets_data(soup) + parse_capes_data(soup)
        all_profs += search_res
        with open(result_file, 'w') as f:
            json.dump(all_profs, f);
        


main() 