"""
This Add-On allows for easy calling of SideKick API from DocumentCloud
"""

import time

from addon import AddOn


class SideKick(AddOn):
    """SideKick Add-On."""

    def initialize_sidekick(self, project_id):
        """Initialize the sidekick instance if it does not exist"""
        self.set_message("Initalizing the SideKick data")
        # create the sidekick on the project
        response = self.client.post(f"projects/{project_id}/sidekick/")

        # check the status
        response = self.client.get(f"projects/{project_id}/sidekick/")
        status = response.json()["status"]
        print(status)

        # keep checking the status until it succeeds
        while status == "pending":
            # wait one minute before checking again
            time.sleep(30)
            response = self.client.get(f"projects/{PROJECT_ID}/sidekick/")
            status = response.json()["status"]
            print(status)

    def parse_project(self, query):
        """Parse the project ID from the search query"""
        pattern = re.compile(r"project:[\w-]+-(\d+)")
        match = query.search(pattern)
        if not match:
            return None
        return int(match.group(1))

    def main(self):
        """Initialize SideKick if necessary and run learning routine"""

        if "tag_name" not in self.data:
            self.set_message("Must provide a tag name")
            return

        tag_name = self.data["tag_name"]
        initialize = self.data.get("initialize", False)
        project_id = self.parse_project(query)

        if project_id is None:
            self.set_message("Must provide a project in the query")
            return

        if initialize:
            # allow the user to specify to force initialization
            self.initialize_sidekick(project_id)
        else:
            response = self.client.get(f"projects/{project_id}/sidekick/")
            if response.status_code == 404:
                # if sidekick instance is not found, we will intialize it
                initialize_sidekick(client, project_id)

        # do the learning!
        self.set_message("Starting the learning process")
        response = self.client.post(
            f"projects/{project_id}/sidekick/learn/", data={"tagname": tag_name}
        )
        print(response.status_code)
        print(response.json())

        # check the status
        response = self.client.get(f"projects/{project_id}/sidekick/")
        status = response.json()["status"]
        print(status)

        # keep checking the status until it succeeds
        while status == "pending":
            # wait ten seconds before checking again
            time.sleep(10)
            response = self.client.get(f"projects/{project_id}/sidekick/")
            status = response.json()["status"]
            print(status)

        self.set_message("Complete")


if __name__ == "__main__":
    SideKick().main()
