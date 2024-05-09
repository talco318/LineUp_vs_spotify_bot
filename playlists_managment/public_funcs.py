# ./playlists_managment/public_funcs.py

import requests


def is_link_valid(link):
    """
    This function checks if a link is valid.

    Returns:
      `True` if the link is valid, `False` if not.
    """

    # Check if the link is empty.
    if not link:
        return False
    try:
        response = requests.get(link)
        # Check if the request was successful.
        print(response.status_code)
        return response.status_code == 200
    except requests.exceptions.HTTPError:
        # The link is not valid.
        return False


def split_links(links: str) -> list[str]:
    """
    Splits a string of links into a list of individual links.

    Args:
        links (str): A string containing one or more links separated by newline characters.

    Returns:
        list[str]: A list of individual links.
    """
    links_list = links.split("\n")  # Split by newline characters
    valid_links = [link.strip() for link in links_list if is_link_valid(link)]  # Filter valid links and remove leading/trailing spaces
    return valid_links


