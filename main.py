"""
This Add-On allows for easy calling of SideKick API from DocumentCloud
"""

import json
import re
import sys
import time

import documentcloud


def load_params():
    """Load the parameters passed in to the GitHub Action."""
    params = json.loads(sys.argv[1])
    # token is a JWT to use to authenticate against the DocumentCloud API
    token = params.pop("token")
    # base_uri is the URI to make API calls to - allows the plugin to function
    # in non-production environments
    base_uri = params.pop("base_uri", None)
    # Documents is a list of document IDs which were selected to run with this
    # plugin activation
    documents = params.pop("documents", None)
    # Query is the search query selected to run with this plugin activation
    query = params.pop("query", None)
    # params will contain add on specific data in 'data', and the user and org
    # IDs in 'user_id' and 'org_id'
    return token, base_uri, documents, query, params


def init():
    """Load the paraneters and initialize the DocumentCloud client."""
    token, base_uri, documents, query, params = load_params()
    kwargs = {"base_uri": base_uri} if base_uri is not None else {}
    client = documentcloud.DocumentCloud(**kwargs)
    client.session.headers.update({"Authorization": "Bearer {}".format(token)})
    client.session.headers["User-Agent"] += " (DC AddOn)"
    return client, documents, query, params


def parse_project(query):
    pattern = re.compile(r"project:[\w-]+-(\d+)")
    match = query.search(pattern)
    if not match:
        return None
    return int(match.group(1))


def initialize_sidekick(client, project_id):
    """Initialize the sidekick instance if it does not exist"""
    # create the sidekick on the project
    response = client.post(f"projects/{project_id}/sidekick/")

    # check the status
    response = client.get(f"projects/{project_id}/sidekick/")
    status = response.json()["status"]
    print(status)

    # keep checking the status until it succeeds
    while status == "pending":
        # wait one minute before checking again
        time.sleep(30)
        response = client.get(f"projects/{PROJECT_ID}/sidekick/")
        status = response.json()["status"]
        print(status)


def main(client, documents, query, params):
    """Initialize SideKick if necessary and run learning routine"""

    if "tag_name" not in params["data"]:
        return

    tag_name = params["data"]["tag_name"]
    initialize = params["data"].get("initialize", False)
    project_id = parse_project(query)

    if initialize:
        # allow the user to specify to force initialization
        initialize_sidekick(client, project_id)
    else:
        response = client.get(f"projects/{project_id}/sidekick/")
        if response.status_code == 404:
            # if sidekick instance is not found, we will intialize it
            initialize_sidekick(client, project_id)

    # do the learning!
    response = client.post(
        f"projects/{project_id}/sidekick/learn/", data={"tagname": tag_name}
    )
    print(response.status_code)
    print(response.json())

    # check the status
    response = client.get(f"projects/{project_id}/sidekick/")
    status = response.json()["status"]
    print(status)

    # keep checking the status until it succeeds
    while status == "pending":
        # wait ten seconds before checking again
        time.sleep(10)
        response = client.get(f"projects/{project_id}/sidekick/")
        status = response.json()["status"]
        print(status)


if __name__ == "__main__":
    args = init()
    main(*args)
