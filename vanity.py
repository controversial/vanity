"""
    _/      _/                      _/    _/
   _/      _/    _/_/_/  _/_/_/        _/_/_/_/  _/    _/
  _/      _/  _/    _/  _/    _/  _/    _/      _/    _/
   _/  _/    _/    _/  _/    _/  _/    _/      _/    _/
    _/        _/_/_/  _/    _/  _/      _/_/    _/_/_/
                                                   _/
                                              _/_/

                                           By Luke Taylor
"""


from datetime import datetime
import getpass
import os
import shutil

import requests


def _semantic_join(items):
    return ", and ".join([", ".join(items)[:-1], items[-1]])


def get(path, params={}):
    """Make an authenticated GET request to the GitHub API."""
    return requests.get(
        os.path.join("https://api.github.com/", path),
        auth=(USER, PASS),
        params=params
    ).json()


# REPOS =======================================================================


def get_my_repos():
    print("- Listing repos")
    repos = []
    page = 0

    # Continue paginating until we hit a page with less than the maximum number
    # of entries
    while True:
        print("- Reading page {} of your repos...".format(page + 1))
        page_repos = get("user/repos", {"page": page, "per_page": 100})
        repos.extend(page_repos)
        if len(page_repos) <= 100:
            break
    print("- Listed repos successfully! Found {} repos.".format(len(repos)))
    return [tuple(repo["full_name"].split("/")) for repo in repos]


def get_my_repo_additions(owner, name):
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


def get_all_repo_additions():
    repos = get_my_repos()
    print("- Reading additions...")
    return {"{}/{}".format(*r): get_my_repo_additions(*r) for r in repos}
    print("- Read additions successfully!")


# GISTS =======================================================================


def get_my_gists():
    print("- Listing gists")
    gists = []
    page = 0

    # Continue paginating until we hit a page with less than the maximum number
    # of entries
    while True:
        print("- Reading page {} of your gists...".format(page + 1))
        page_gists = get("gists", {"page": page, "per_page": 100})
        gists.extend(page_gists)
        if len(page_gists) <= 100:
            break
    print("- Listed gists successfully! Found {} gists.".format(len(gists)))
    return [gist["id"] for gist in gists]


def get_all_gist_additions():
    """Get the sum of the additions made in all revisions from the last year.

    In a single comprehension!
    """
    print("Calculating additions...")
    return {
        # Total additions in the last year
        _semantic_join(list(gist["files"].keys())): sum(
            rev["change_status"].get("additions", 0) for rev in gist["history"]
            if (
                datetime.strptime(rev["committed_at"], "%Y-%m-%dT%H:%M:%SZ")
                - datetime.now()).days <= 360
        )
        # For each gist
        for gist in (get("gists/" + gist_id) for gist_id in get_my_gists())
    }


# MAIN ========================================================================


def auth(username=None, password=None):
    global USER, PASS
    if not (username and password):
        username = input("GitHub Username: ")
        password = getpass.getpass("GitHub Password: ")
    USER = username
    PASS = password

    print("- Authenticating...", end=" ")

    if get("").get("message") == "Bad credentials":
        print()
        raise ValueError("Invalid login.")
    else:
        print("- Success!")


if __name__ == "__main__":
    print(__doc__)

    auth()

    print()
    repo_adds = get_all_repo_additions()
    print()
    gist_adds = get_all_gist_additions()
    total_adds = sum(repo_adds.values()) + sum(gist_adds.values())

    terminal_width = shutil.get_terminal_size()[0]
    # PRINT RESULTS

    print("\n\n\nTotal additions: {}".format(total_adds).ljust(terminal_width))
    print("\n")

    print("REPOS: {} additions ".format(
        sum(repo_adds.values())
    ).ljust(terminal_width, "-"))
    print()
    print("\n".join([
        "{}. {}: {} lines".format(i + 1, *repo) for i, repo in enumerate(
            sorted(repo_adds.items(), key=lambda x: x[1], reverse=True)
        )
    ][:10]))

    print("\n")

    print("GISTS: {} additions ".format(
        sum(gist_adds.values())
    ).ljust(terminal_width, "-"))
    print()
    print("\n".join([
        "{}. {}: {} lines".format(i + 1, *gist) for i, gist in enumerate(
            sorted(gist_adds.items(), key=lambda x: x[1], reverse=True)
        )
    ][:10]))
