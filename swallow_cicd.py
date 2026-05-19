# coming soon...

# TODO: Rewrite for CI/CD pipeline

"""
    message = "Do you want to commit the changes? (y/n): "
    if input(message).lower() == "y":
        self.commit_changes(args.mode)
        is_commited = True

    if args.mode != "4":
        message = "Do you want to regenerate sitemap as well? (y/n): "
        if args.sitemap == "y" or input(message).lower() == "y":
            self.regenerate_sitemap()
            if is_commited:
                message = "Do you want to commit the sitemap changes? (y/n): "
                if input(message).lower() == "y":
                    self.commit_changes("4")

    if is_commited:
        message = "Do you want to push the changes to remote? (y/n): "
        if input(message).lower() == "y":
            self.push_changes()
"""


"""
    def commit_changes(self, mode):
        repo = Repo(self.settings["to"])
        repo.git.add(all=True)
        if not repo.index.diff("HEAD"):
            print("No changes detected to commit.")
            return
        match mode:
            case "1":
                message = (
                    'Auto-Generated: Add new article '
                    f'"{self.article_id}" and regenerate index')
            case "2":
                message = 'Auto-Generated: Regenerate index'
            case "3":
                message = 'Auto-Generated: Regenerate all articles and index'
            case "4":
                message = 'Auto-Generated: Regenerate sitemap'
            case _:
                raise ValueError("Invalid mode.")
        repo.git.commit("-S", m=message)
        print(f"Changes committed with message: '{message}'.")

    def push_changes(self):
        repo = Repo(self.settings["to"])
        current_branch = repo.active_branch
        upstream = current_branch.tracking_branch()
        if upstream is None:
            print(
                f"No upstream branch set for {current_branch}."
                "Please set it before pushing.")
            return
        unpushed_commits = list(
            repo.iter_commits(f"{upstream.name}..{current_branch.name}"))
        if not unpushed_commits:
            print("No commits to push.")
            return
        origin = repo.remote(name=self.settings["to_remote"])
        origin.push()
        print("Changes have been pushed to the remote repository.")
"""
