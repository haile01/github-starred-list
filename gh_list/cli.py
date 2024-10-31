from gh_list import ListHandler
import argparse

def main():
    parser = argparse.ArgumentParser(description="GitHub Starred List CLI")
    parser.add_argument("action", choices=["create", "add", "remove", "delete"], help="Action to perform")
    parser.add_argument("--user", required=True, help="GitHub username")
    parser.add_argument("--cookie", required=True, help="GitHub cookie string")
    parser.add_argument("--list", help="Name of the list")
    parser.add_argument("--desc", help="Description of the list")
    parser.add_argument("--repo", help="Repository name")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    handler = ListHandler(user=args.user, cookie=args.cookie, debug_mode=args.debug)

    if args.action == "create":
        handler.create_list(name=args.list, desc=args.desc)
    elif args.action == "add":
        handler.add_repo(repo=args.repo, _list=args.list)
    elif args.action == "remove":
        handler.remove_repo(repo=args.repo, _list=args.list)
    elif args.action == "delete":
        handler.delete_list(_list=args.list)

if __name__ == "__main__":
    main()