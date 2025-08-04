import csv

from classes.utils.WPPaths import WPPaths


class Project:
    def __init__(self, theme_name):
        self.theme_name = theme_name
        self.project = self.getProject()

    def getProject(self):
        projects = ()
        csv_file_path = WPPaths.get_list_csv_path()
        with open(csv_file_path) as my_file:
            reader = csv.reader(my_file, delimiter=",")
            for row in reader:
                project = {
                    "title": row[0],
                    "login": row[1],
                    "password": row[2],
                    "url": row[3],
                }
                if len(row) > 4:
                    project["gestione"] = row[4]
                projects = projects + (project,)
        theme_is_in_projects = [
            project for project in projects if project["title"] == self.theme_name
        ]
        if not theme_is_in_projects:
            print("[red]Theme is not in projects")
            exit(1)
        else:
            return theme_is_in_projects[0]

    def getLoginUrl(self, second_param=True):
        project_url = self.project["url"]
        if second_param:
            return f"{project_url}/wp-admin"
        else:
            if "gestione" not in self.project:
                return f"{project_url}/gestione"
            else:
                return f"{project_url}/{self.project['gestione']}"
