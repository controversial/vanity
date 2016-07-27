# How many lines of code have you committed to GitHub in all time?

import getpass
import json
import os

import requests

USER = input("GitHub Username: ")
PASS = getpass.getpass("GitHub Password: ")


def get(path, params={}):
    return json.loads(requests.get(
        os.path.join("https://api.github.com/", path),
        auth=(USER, PASS),
        params=params
    ).text)


def get_my_repos():
    repos = []
    page = 0

    # Continue paginating until we hit a page with less than the maximum number
    # of entries
    while True:
        print("Reading page {} of user repos".format(page + 1))
        page_repos = get("user/repos", {"page": page, "per_page": 100})
        repos.extend(page_repos)
        if len(page_repos) <= 100:
            break

    return [tuple(repo["full_name"].split("/")) for repo in repos]


def get_my_additions(owner, name):
    print("Reading additions to {}/{}...".format(owner, name))
    contributions = get("repos/{}/{}/stats/contributors".format(owner, name))
    # Find the authenticated user's contributions
    try:
        my_contributions = [
            c for c in contributions if c["author"]["login"] == USER
        ][0]
        total = sum([week["a"] for week in my_contributions["weeks"]])
    except IndexError:
        # The user has made no contributions to this repo
        total = 0
    print("{} lines".format(total))
    return total


def get_total_additions():
    return sum(get_my_additions(owner, name) for owner, name in get_my_repos())


if __name__ == "__main__":
    print(get_total_additions())
