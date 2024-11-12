import os
import sys
import json
import csv
from seeker import Colour, search_email
from tkinter import Tk, filedialog  # Import tkinter for file selection

CONFIG_FILE = "config.json"


# Load the current configuration from JSON
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"search_engine": "ddg", "search_mode": "requests"}  # default settings


# Save the configuration to JSON
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)


def logo():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Colour.Magenta + "\033[1m▒▒▒▒▒ SEEKER ▒▒▒▒▒\033[0m")
    print()


def main_menu():
    try:
        print(Colour.Yellow + "\033[1mMain menu:\033[0m")
        print(Colour.Yellow + "\033[1m[1] - Emails from single keyword\033[0m")
        print(Colour.Yellow + "\033[1m[2] - Emails from list (.csv)\033[0m")
        print(Colour.Yellow + "\033[1m[0] - Exit\033[0m")
        print()
        print(Colour.Yellow + "\033[1m[s] - Switch URL search engine1\033[0m")
        print(Colour.Yellow + "\033[1m[p] - Switch prompt mode\033[0m")
        print(Colour.Yellow + "\033[1m[i] - Instructions\033[0m")
        print()

        config = load_config()  # Load configuration at the start

        choice = input(Colour.Yellow + "\033[1m=> \033[0m")

        if choice == "1":
            keyword = input("\033[1mEnter keyword (for example 'example.com'): \033[0m")
            search_email(keyword)
            main_menu()

        if choice == "2":
            # Open a file dialog to select the .csv file with keywords
            root = Tk()
            root.withdraw()  # Hide Tkinter root window
            filename = filedialog.askopenfilename(title="Select CSV file with keyword list",
                                                  filetypes=[("CSV files", "*.csv")])

            if filename and os.path.exists(filename):  # Proceed if a file was selected
                with open(filename, 'r', encoding="utf-8") as file:
                    reader = csv.reader(file)
                    keywords = [row[0].strip() for row in reader if row]  # Load keywords from the first column
                    for keyword in keywords:
                        search_email(keyword)
                print("\033[1mProcessing complete. Results saved in emails.csv\033[0m")
            else:
                print(Colour.Red + "File not found or not selected. Please try again.")
            main_menu()

        if choice == "0":
            print("\033[1mGoodbye!\033[0m")
            sys.exit()

        elif choice == "s":
            print("\033[1mSelect search engine. Every engine brings different results:\033[0m")
            print(Colour.Yellow + "\033[1m'1'" + Colour.White + " - Google (API)\033[0m")
            print(Colour.Yellow + "\033[1m'2'" + Colour.White + " - DuckDuckGo\033[0m")
            print(Colour.Yellow + "\033[1m'Enter'" + Colour.White + " to return to main menu.\033[0m")
            key = input(Colour.Yellow + "\033[1m=> \033[0m")
            if key == "1":
                config["search_engine"] = "g_api"
            elif key == "2":
                config["search_engine"] = "ddg"
            else:
                logo()
                main_menu()
                return
            save_config(config)
            logo()
            print(f"\033[1mSearch engine set to {config['search_engine']}.\033[0m")
            main_menu()

        elif choice == "p":
            print("\033[1mSelect prompt usage. Influences the result, speed and query limits.\033[0m")
            print(Colour.Yellow + "\033[1m'1'" + Colour.White + " - 'Keyword'\033[0m")
            print(Colour.Yellow + "\033[1m'2'" + Colour.White + " - 'site:Keyword'\033[0m")
            print(Colour.Yellow + "\033[1m'3'" + Colour.White + " - Both\033[0m")
            print(Colour.Yellow + "\033[1m'Enter'" + Colour.White + " to return to main menu.\033[0m")
            key = input(Colour.Yellow + "\033[1m=> \033[0m")
            if key == "1":
                config["prompt_mode"] = "keyword"
            elif key == "2":
                config["prompt_mode"] = "site"
            elif key == "3":
                config["prompt_mode"] = "both"
            else:
                logo()
                main_menu()
                return
            save_config(config)
            logo()
            print(f"\033[1mPrompt usage set as '{config['prompt_mode']}'.\033[0m")
            main_menu()

        elif choice == "i":
            print("\033[1mBoolean search automation for your target's email.\033[0m")
            print(Colour.Yellow + "\033[1m'Enter'" + Colour.White + " to return to main menu.\033[0m")
            input(Colour.Yellow + "\033[1m=> \033[0m")
            logo()
            main_menu()

        else:
            logo()
            main_menu()
    except KeyboardInterrupt:
        logo()
        print("Script interrupted by user.")
        main_menu()


# STARTING SCRIPT:

if __name__ == "__main__":
    logo()
    main_menu()
