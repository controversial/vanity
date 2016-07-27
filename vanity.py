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
        print("- Reading page {} of user repos...".format(page + 1))
        page_repos = get("user/repos", {"page": page, "per_page": 100})
        repos.extend(page_repos)
        if len(page_repos) <= 100:
            break
    print("- Listed repos successfully!")
    return [tuple(repo["full_name"].split("/")) for repo in repos]


def get_my_additions(owner, name):
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
    return total


def get_total_additions():
    repos = get_my_repos()
    print("- Reading additions...")
    by_repo = {}
    for owner, name in repos:
        by_repo["{}/{}".format(owner, name)] = get_my_additions(owner, name)
    return sum(by_repo.values()), by_repo


if __name__ == "__main__":
    adds = get_total_additions()
    print("\n\n\nTotal additions: ", adds[0])
    print("----------------------------------")
    print("REPOS ----------------------------")
    for name, lines in sorted(adds[1].items(), key=lambda x: x[1])[::-1]:
        print(name+":", lines, "lines | ", end="")
