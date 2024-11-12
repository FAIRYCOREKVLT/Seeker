import re
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from googlesearch import search
import csv
import json

CONFIG_FILE = "config.json"


# COLOURS FOR TEXT:
class Colour:
    Green = "\u001b[32m"
    Yellow = "\u001b[33m"
    Blue = "\u001b[34m"
    Magenta = "\u001b[35m"
    White = "\u001b[37m"
    Red = "\u001b[31m"


# Load configuration from JSON file
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"search_engine": "ddg", "search_mode": "requests"}  # default values


# Function to save data to a CSV file
def save_to_csv(data, filename="emails.csv"):
    headers = ["query", "email", "page"]
    with open(filename, 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Add headers only if file is empty
            writer.writerow(headers)
        for entry in data:
            writer.writerow(entry)


# SEARCH FUNCTION BASED ON JSON CONFIG
def url_search(query):
    config = load_config()
    search_engine = config.get("search_engine", "ddg")

    if search_engine == "no_g_api":  # Regular Google search
        results_list = []
        for result in search(query):
            results_list.append(result)
        return results_list

    elif search_engine == "g_api":  # Google API search
        api_key = config.get("google_api_key", "")
        search_engine_id = config.get("google_search_engine_id", "")
        search_url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query
        }
        response = requests.get(search_url, params=params)

        # results
        results_list = []
        if response.status_code == 200:
            data = response.json()
            links = [item.get("link") for item in data.get('items', [])]
            for link in links:
                results_list.append(link)
        else:
            print(f"error sending request: {response.status_code}")
        return results_list

    elif search_engine == "ddg":  # DuckDuckGo search
        with DDGS() as ddgs:
            results_list = [link['href'] for link in ddgs.text(query)]
            return results_list


def email_parsing(query):
    if "application/xml" in query.headers.get("Content-Type", ""):
        soup = BeautifulSoup(query.content, "lxml-xml")
    else:
        soup = BeautifulSoup(query.content, "html5lib")
    email_list = []  # addresses from single URL
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'
    for link in soup.find_all():
        text = link.get_text()
        matches = re.findall(email_regex, text)

        for match in matches:
            wrong_match_regex_list = [
                r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:png|jpg|jpeg|bmp|tga|svg)',
                r'^[a-f0-9]{32}@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}$',
                r'^[A-Za-z0-9._%+-]+@[0-9A-Za-z.-]+x?\.(?:png|jpg|jpeg|bmp|tga|svg)$',
                r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:ingest|error-tracking)\.sentry\.io$',
                r'[A-Za-z0-9._%+-]+@(?:error-tracking|tracking|ingest)\.[A-Za-z0-9.-]+'
            ]
            if any(re.match(regex, match) for regex in wrong_match_regex_list):
                continue

            is_unique = True
            for existing_email, url in email_list:
                if match in existing_email or existing_email in match:
                    if len(existing_email) <= len(match):
                        is_unique = False
                        break
                    email_list.remove((existing_email, url))
                    break

            # Добавить, если уникален
            if is_unique:
                email_list.append((match, query.url))

    return email_list


def search_email(keyword):
    try:
        public_domains = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "zoho.com", "zohomail.eu",
                          "protonmail.com", "proton.me", "icloud.com", "mail.com", "mail.ru", "yandex.ru", "ukr.net"]
        if keyword in public_domains:
            print("lol okay good luck with it")
            return
        else:
            request_site = f'site:{keyword}'
            request_keyword = f'"{keyword}"'

            print(f"\033[1m{keyword}: getting URLs...\033[0m", end="\n\n")

            url_list_site = []
            url_list_keyword = []

            config = load_config()
            prompt_usage = config.get("prompt_mode", "")

            if prompt_usage == "site" or prompt_usage == "both":
                try:
                    url_list_site = url_search(request_site)
                except Exception:
                    pass

            if prompt_usage == "keyword" or prompt_usage == "both":
                try:
                    url_list_keyword = url_search(request_keyword)
                except Exception:
                    pass

            url_list = list(set(url_list_site + url_list_keyword))

            print("\033[1mURLs: \033[0m", end="\n\n")
            unique_emails = set()  # Set to store unique emails
            all_emails = []  # Collecting emails for CSV export

            for num, result in enumerate(url_list, start=1):
                print(f"\033[1m{num}.\033[0m {result}")

            print(f"\033[1m{keyword}: getting e-mails. Please wait...\033[0m", end="\n\n")
            for result in url_list:
                try:
                    email_data = email_parsing(requests.get(result, timeout=60))
                    for email, source in email_data:
                        if email not in unique_emails:  # Only add if email is unique
                            unique_emails.add(email)
                            all_emails.append((keyword, email, source))
                except requests.exceptions.Timeout:
                    print(f"Timeout 60s: skipping {result}")
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching URL {result}: {e}")

            if not all_emails:  # new
                all_emails.append((keyword, "-", "-"))

            save_to_csv(all_emails)  # Exporting to CSV
            for num, result in enumerate(all_emails, start=1):
                print(f"\033[1m{num}.\033[0m {result[1]}")

            print("\033[1mSearch finished, check 'emails.csv'\033[0m", end="\n\n")

    except Exception as e:
        print(f"Error for {keyword}: {e}")
