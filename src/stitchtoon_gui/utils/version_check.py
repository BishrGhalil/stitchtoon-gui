# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.

import requests


try:
    from packaging.version import parse as parse_version
except ImportError:
    from pkg_resources import parse_version
except ImportError:

    def parse_version(version: str) -> tuple[int, int, int]:
        import re

        version_tuple = ()
        regexp = r"[V-v]?(\d\d?)\.(\d\d?)\.?(\d\d?)?"
        matches = re.search(regexp, version)
        if not matches:
            return (0, 0, 0)
        for group in matches.groups():
            try:
                version_tuple += (int(group),)
            except ValueError:
                continue

        return version_tuple


__repos = [
    {
        "name": "pypi.org",
        "needs": ["package"],
        "url": "https://pypi.org/pypi/{package}/json",
        "headers": {},
        "parsing_flow": ["releases"],
        "callback": lambda releases_dict: parse_version(
            max(releases_dict.keys(), key=lambda x: parse_version(x))
        ),
    },
    {
        "name": "github",
        "needs": ["package", "org"],
        "url": "https://api.github.com/repos/{org}/{package}/releases/latest",
        "headers": {
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        },
        "parsing_flow": ["tag_name"],
        "callback": lambda version_tag: parse_version(version_tag),
    },
]


def get_repo_version(package: str, org: str = "", default=None):
    for repo in __repos:
        if "org" in repo["needs"] and not org:
            continue
        res = requests.get(
            repo["url"].format(package=package, org=org), headers=repo["headers"]
        )
        if res.status_code == 200:
            json_res = res.json()
            for key in repo["parsing_flow"]:
                json_res = json_res[key]
            return (repo["name"], str(repo["callback"](json_res)))
        else:
            continue
    return default
