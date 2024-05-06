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
        return response.status_code == 200
    except requests.exceptions.HTTPError:
        # The link is not valid.
        return False
