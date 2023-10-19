# FILE: IO functions


# DEPENDENCIES
import common
from datetime import datetime
import json


# VARIABLES
log_file_buffer = []  # Buffer to write to file


# FUNCTIONS
def log(ticker: str = "INFO",
        message: str = "(No message provided)",
        timestamp: bool = True,
        to_console: bool = True,
        to_file: bool = True) -> None:

    # FUNCTION: Log to console and log file

    # PARAMS:
    #   * ticker: str: Ticker to display
    #   * message: str: Message to display
    #   * timestamp: bool: Whether to include timestamp
    #   * to_console: bool: Whether to print to console
    #   * to_file: bool: Whether to write to log file

    # RETURNS:
    #   * (print): Print message
    #   * (variable set): Add to log_file_buffer

    # Define globals
    global log_file_buffer

    # Create output
    output = ""
    if timestamp:
        output += f"({datetime.now()})\t"
    output += f"[{ticker.upper()}]\t"
    output += f"{message.capitalize()}\t"

    # Print to console
    if to_console:
        print(output)

    # Add to file buffer
    if to_file:
        log_file_buffer.append(output)


def update_log_file(file_path: str = common.LOG_FILE_PATH) -> None:

    # FUNCTION: Write buffer to log file

    # PARAMS:
    #   * file_path: str: Path where log file is stored

    # RETURNS:
    #   * (file output): Write to file

    # Log
    log(ticker="io",
        message=f"Updating log file at '{file_path}'...")

    # Define globals
    global log_file_buffer

    # Duplicate file buffer and clear original
    buffer = log_file_buffer
    log_file_buffer = []

    # Write to file
    file = open(file_path, "a")
    file.writelines(f"{line}\n" for line in buffer)
    file.close()

    # Log
    log(ticker="io",
        message=f"Updated log file at '{file_path}'.")


def read_json(file_path: str) -> dict:

    # FUNCTION: Parse json file into dict

    # PARAMS:
    #   * file_path: str: Path to json file

    # RETURNS:
    #   * result: dict: Json from file parsed into dict

    # Log
    log(ticker="io",
        message=f"Reading json from '{file_path}'...")

    # Open json file and parse
    with open(file_path, "r") as file:
        result = json.load(file)

    # Log
    log(ticker="io",
        message=f"Read json from '{file_path}'.")

    # Return resulting dict
    return result


def write_json(file_path: str,
               data: dict) -> None:

    # FUNCTION: Write dictionary to file in json format

    # PARAMS:
    #   * file_path: str: Path to json file
    #   * data: dict: Dict to parse into json

    # RETURN:
    #   * (file output): Write to file

    # Log
    log(ticker="io",
        message=f"Writing data to '{file_path}'...")

    # Write json to file
    with open(file_path, "w") as file:
        json.dump(data,
                  file,
                  indent=4)

    # Log
    log(ticker="io",
        message=f"Wrote data to '{file_path}'.")


# TESTING
if __name__ == "__main__":
    write_json(data={"a": 1, "b": 3, "c": {"aa": 11, "bb": 33}, "d": 5}, file_path="data/test.json")
