from gh_list import ListHandler
import os

def random_name(existing=[]):
    name = "test" + os.urandom(2).hex()
    while name in existing:
        name = "test" + os.urandom(2).hex()

    return name

if __name__ == "__main__":
    username = "haile01"
    repo_name = "codeigniter4/shield"
    cookie = os.environ["GH_STAR_LIST_COOKIE"]

    helper = ListHandler(username, cookie)
    existing_lists = list(helper.available_lists(raw=True))
    print("Start testing")
    print("Existing lists:", existing_lists)
    print("Usual flow")
    list_name = random_name()
    desc = list_name + " desc"
    helper.create_list(list_name, desc)
    input(f"| Observe that list {list_name} is created. Enter to continue")
    helper.add_repo(repo_name, list_name)
    input(f"| Observe that repo {repo_name} is added to list {list_name}. Enter to continue")
    helper.remove_repo(repo_name, list_name)
    input(f"| Observe that repo {repo_name} is removed from list {list_name}. Enter to continue")
    helper.delete_list(list_name)
    input(f"| Observe that list {list_name} is deleted. Enter to continue")

    print("\n| Done\n-----")

    print("Remove non-existent list")
    try:
        helper.delete_list("a vezi, vezy long list name that really should'nt be made by anyone")
    except Exception as e:
        assert str(e) == "Can get token, list a-vezi-vezy-long-list-name-that-really-should-nt-be-made-by-anyone doesn't exist"

    print("= Duplicated list =")
    try:
        helper.create_list(existing_lists[0], "desc")
    except Exception as e:
        assert e == f"List {existing_lists[0]} already exists"

    print("\n| Done\n-----")

    print("= List limit =")
    temp_lists = []
    print("| Creating dummy lists, might take a while...")
    for _ in range(helper.GH_REPO_LIMIT - len(existing_lists)):
        list_name = random_name(existing=temp_lists)
        temp_lists.append(list_name)
        helper.create_list(list_name, list_name + " desc")

    try:
        list_name = random_name(existing=temp_lists)
        helper.create_list(list_name, list_name + " desc")
    except Exception as e:
        assert str(e) == f"GitHub limit reached, can't create more than {helper.GH_REPO_LIMIT} lists"

    print("| Removing dummy lists, might take a while...")
    for _list in temp_lists:
        helper.delete_list(_list)

    print("\n| Done\n-----")

    print("Looking good")
