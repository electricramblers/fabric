#!/usr/bin/env python

import os
import importlib.util
import ipaddress
import socket
import openai
import requests
from dotenv import load_dotenv, set_key, get_key
from termcolor import colored
from distutils.util import strtobool


def environment_variable_boolean(key):
    DOTENV_PATH = ".env"
    value_string = get_key(DOTENV_PATH, key)
    return bool(strtobool(value_string))


def get_yes_or_no():
    valid_input = False
    while not valid_input:
        user_input = (
            input(colored("Please enter 'y' for yes or 'n' for no: ", "green"))
            .lower()
            .strip()
        )
        if user_input == "y":
            valid_input = True
            return True
        elif user_input == "n":
            valid_input = True
            return False
        else:
            print(
                colored("Invalid input. Please enter 'y' for yes or 'n' for no.", "red")
            )


def check_ollama_installed(dotenv_path):
    package_name = "ollama"
    ollama_spec = importlib.util.find_spec(package_name)
    if ollama_spec is not None:
        print(colored("Ollama is installed locally. Do you want to use it?", "green"))
        if get_yes_or_no():
            try:
                set_key(config_file, key_to_set="LOCAL_OLLAMA", value_to_set="True")
            except Exception as err:
                print(colored(f"An error occured: {err}", "red"))
    else:
        try:
            set_key(
                dotenv_path,
                "LOCAL_OLLAMA",
                "False",
            )
            print(colored("Ollama is not installed locally.", "cyan"))
        except Exception as err:
            print(colored(f"An error occured: {err}", "red"))
    print(
        colored(
            "\nYou can also connect to a computer on your network that is running ollama.",
            "green",
        )
    )
    while True:
        port = 11434
        ip_address = input(
            colored(
                "Enter the IP address of that computer or leave blank and press enter.\nIP: ",
                "green",
            )
        )
        if not ip_address:
            print("The IP address is blank.")
            try:
                set_key(
                    dotenv_path,
                    "REMOTE_OLLAMA",
                    "False",
                )
                break
            except:
                print(colored("I set REMOTE_OLLAMA to False", "cyan"))
                break
        else:
            try:
                ipaddress.ip_address(ip_address)
                print(colored(f"{ip_address} is a valid IP address", "green"))
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(2)
                        result = s.connect_ex((ip_address, port))
                        if result == 0:
                            print(f"Port {port} on {ip_address} is open.")
                            set_key(
                                dotenv_path,
                                "REMOTE_OLLAMA",
                                "True",
                            )
                            print(colored("Setting REMOTE_OLLAMA to True", "cyan"))
                            break
                        else:
                            print(
                                colored(
                                    f"Port 11434 on {ip_address} is not open.\n", "red"
                                )
                            )
                except socket.error as err:
                    print(f"Socket error: {err}")
            except ValueError:
                print(colored(f"{ip_address} is not a valid IP address.\n", "red"))
    set_key(DOTENV_PATH, "FIRST_RUN", "False")
    set_key(DOTENV_PATH, "LLM_CONFIGURED", "False")


def ai_agent():
    DOTENV_PATH = ".env"
    set_key(DOTENV_PATH, "FIRST_RUN", "True")

    def is_openrouter_api_key_valid(api_key):
        url = "https://openrouter.ai/api/v1/auth/key"
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def is_openai_api_key_valid(api_key):
        openai.api_key = api_key
        try:
            openai.Engine.list()
            return True
        except openai.error.OpenAIError as e:
            print(f"An error occurred: {e}")
            return False

    while True:
        try:
            if not environment_variable_boolean(
                "FIRST_RUN"
            ) and environment_variable_boolean("LLM_CONFIGURED"):
                break
            else:
                print(colored(DOTENV_PATH, "white"))
                check_ollama_installed(DOTENV_PATH)
                if environment_variable_boolean("FIRST_RUN"):
                    break
        except Exception as err:
            print(colored(f"Line 152 -An error occured: {err}", "red"))
    while True:
        try:
            choice = int(input("Enter 1 for openrouter or 2 for openai: "))
            if choice == 1:
                external_llm = "openrouter"
                openrouter_api_key = input(
                    colored("Enter openrouter api key: ", "yellow")
                )
                if is_openrouter_api_key_valid(openrouter_api_key):
                    set_key(DOTENV_PATH, "EXTERNAL_LLM", external_llm)
                    break
                else:
                    print(colored("The api key is invalid.", "red"))
            elif choice == 2:
                external_llm = "openai"
                openai_api_key = input(colored("Enter OpenAI API Key: ", "yellow"))
                if is_openai_api_key_valid(openai_api_key):
                    set_key(DOTENV_PATH, "EXTERNAL_LLM", external_llm)
                    break
                else:
                    print(colored("The api key is invalid.", "red"))
            else:
                print(colored("Invalid choice. Please enter 1 or 2.", "cyan"))
        except ValueError:
            print(colored("Invalid input. Please enter an integer.", "red"))


# -------------------------------------------------------------------------------
# Here Be Dragons
# -------------------------------------------------------------------------------
def main():
    os.system("clear")
    ai_agent()


if __name__ == "__main__":
    main()
