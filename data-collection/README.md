# Data collection module

Requires Python 3.11 and higher due to some typing features not available in
earlier versions.

## Installation

A virtual environment is highly recommended. Install required dependency (playwright)
using the following command:

```sh
pip install -r requirements.txt
```

## Execution

There are 3 available scripts:

-   `get_hotel_list.py`: Gets a list of hotel details page on Google Travel based on the given list of locations, then writes to a plain text file, one URL a line.

-   `get_hotel_details.py`: Gets a list of hotel details, listed in a list of URLs acquired from `get_hotel_list.py` script, then writes to a CSV file.

-   `get_hotel_reviews.py`: Gets a list of user reviews, listed in a list of URLs acquired from `get_hotel_list.py` script, then writes to a CSV file.

Check out the usage by running `python script_to_use.py -h` for more details.

## License

This module is licensed under the same license as the parent repository.
