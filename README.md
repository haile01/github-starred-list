## Github starred list
Some low-effort effort to automate categorizing starred repos on Github cuz RestAPI ain't gonna do that anytime soon

### How to?
Initialize with github username and cookie header grabbed from `https://github.com/<urname>?tab=stars`
*Yep that would only last for 2 weeks sorry*

Use 4 methods like in the example:
- `create_list(list_name, list_desc)`
- `add_repo(repo_name, list_name)`
- `remove_repo(repo_name, list_name)`
- `delete_list(repo_name)`

### But... Python Object Oriented Programming?
Yup I hate that but I'm lazy, and it's intended to be imported elsewhere.
