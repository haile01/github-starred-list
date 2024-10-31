import requests
import re

class ListHandler:
  """
  Handles operations related to GitHub starred repositories lists, 
  such as creating, adding, removing, and deleting lists.
  
  Attributes:
    HOST (str): The base URL for GitHub.
    CSRF_TOKEN_PATTERN (str): Regex pattern to find CSRF token in HTML.
    REPO_ID_PATTERN (str): Regex pattern to find repository ID in HTML.
    HEADERS (dict): Default headers for HTTP requests.
    debug_mode (bool): Flag to enable debug mode.
    user (str): GitHub username.
    cookies (dict): Parsed cookies for authentication.
  Methods:
    __init__(user, cookie, debug_mode=False):
      Initializes the ListHandler with the given user, cookie, and debug mode.
    __debug(*args):
      Prints debug information if debug mode is enabled.
    __parse_cookie(cookie_str):
      Parses a cookie string into a dictionary.
    __init_requests():
      Initializes the GET and POST request methods with default headers and cookies.
    __search_before_text(s, pattern, text):
      Searches for a pattern in a string before a specified text.
    __get_list_mapping_and_token(repo):
      Retrieves the list mapping and CSRF token for a given repository.
    __get_repo_id(repo):
      Retrieves the repository ID for a given repository.
    __repo_to_list(repo, _list, add=True):
      Adds or removes a repository to/from a list.
    create_list(name, desc):
      Creates a new list with the given name and description.
    add_repo(repo, _list):
      Adds a repository to a specified list.
    remove_repo(repo, _list):
      Removes a repository from a specified list.
    delete_list(_list):
      Deletes a specified list.
  Usage:
    handler = ListHandler(user="username", cookie="cookie_string", debug_mode=True)
    handler.create_list(name="My List", desc="Description of my list")
    handler.add_repo(repo="repo_name", _list="My List")
    handler.remove_repo(repo="repo_name", _list="My List")
    handler.delete_list(_list="My List")
  """
  def __init__(self, user, cookie, debug_mode=False):
    self.HOST = "https://github.com"
    self.CSRF_TOKEN_PATTERN = r'<input type="hidden" name="authenticity_token" value="(.+?)" autocomplete="off" />'
    self.REPO_ID_PATTERN = r'<input type="hidden" name="repository_id" value="([0-9]+)">'

    self.debug_mode = debug_mode
    self.user = user
    self.__get, self.__post = self.__init_requests(cookie)

  def __debug(self, *args):
    if self.debug_mode:
      print("[github-starred-list]", *args)

  def __parse_cookie(self, s):
    cookies = {}
    for c in s.split(';'):
      try:
        name, value = c.strip().split('=')
      except:
        print(f"Error parsing cookie: {c}, should be in format 'name=value'")
        continue
      cookies[name] = value
    return cookies

  def __init_requests(self, cookie):
    headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.71 Safari/537.36",
      "Accept": "text/html, application/json",
      "Accept-Encoding": "gzip, deflate, br",
      "Accept-Language": "en-US,en;q=0.9",
      "Content-Type": "application/x-www-form-urlencoded",
      "X-Requested-With": "XMLHttpRequest",
      "Origin": "https://github.com"
    }

    self.cookies = self.__parse_cookie(cookie)

    def get(path, *args, **kwargs):
      self.__debug('get', args, kwargs)
      return requests.get(self.HOST + path, *args, **kwargs, cookies=self.cookies)

    def post(path, *args, **kwargs):
      self.__debug('post', args, kwargs)
      return requests.post(self.HOST + path, *args, **kwargs, headers=headers, cookies=self.cookies)

    return get, post

  def __search_before_text(self, s, pattern, text):
    ind = s.find(text)
    if ind != -1:
      s = s[:ind]

    found = re.findall(pattern, s)
    if len(found) == 0:
      return None

    return found[-1]

  def __get_list_mapping_and_token(self, repo):
    mapping = {}
    r = self.__get(f'/{repo}/lists')

    pattern = r"""<input
                    type="checkbox"
                    class="mx-0 js-user-list-menu-item"
                    name="list_ids\[\]"
                    value="([0-9]+)"
                    (?:checked)?
                  >
                  <span data-view-component="true" class="Truncate ml-2 text-normal f5">
    <span data-view-component="true" class="Truncate-text">(.+?)</span>"""

    found = re.findall(pattern, r.text, re.MULTILINE)
    for l in found:
      mapping[l[1]] = l[0]

    # token
    found = re.findall(self.CSRF_TOKEN_PATTERN, r.text)

    return mapping, found[0]

  def __get_repo_id(self, repo):
    r = self.__get(f'/{repo}/lists')
    found = re.findall(self.REPO_ID_PATTERN, r.text)
    assert len(found) > 0, "Repo doesn't exist"

    return found[0]

  def __repo_to_list(self, repo, _list, add=True):
    mapping, token = self.__get_list_mapping_and_token(repo)
    assert _list in mapping, "List doesn't exist"

    list_id = mapping[_list]

    data = {
      "_method": "put",
      "authenticity_token": token,
      "repository_id": self.__get_repo_id(repo),
      "context": "user_list_menu",
      "list_ids[]": list_id if add else ""
    }

    r = self.__post(f'/{repo}/lists', data=data)
    assert r.status_code == 200, f"Failed, please check your cookies again {self.cookies}"

  def create_list(self, name, desc):
    r = self.__get(f'/{self.user}?tab=stars')
    token = self.__search_before_text(r.text, self.CSRF_TOKEN_PATTERN, "Create a list to organize your starred repositories.")
    assert token is not None, "Can get token"

    data = {
      "authenticity_token": token,
      "user_list[name]": name,
      "user_list[description]": desc
    }

    r = self.__post(f'/stars/{self.user}/lists', data=data)
    assert r.status_code == 200, f"Failed, please check your cookies again {self.cookies}"

  def add_repo(self, repo, _list):
    self.__repo_to_list(repo, _list)

  def remove_repo(self, repo, _list):
    self.__repo_to_list(repo, _list, add=False)

  def delete_list(self, _list):
    def preprocess(s):
      s = re.sub(r'[^\w\s]', '', s) # remove special chars
      s = s.lower().strip() # lower case and remove leading/trailing spaces
      s = re.sub(r'\s+', ' ', s) # combine multiple spaces into one
      s = s.replace(' ', '-') # replace space with dash
      return s
    
    _list = preprocess(_list)
    r = self.__get(f'/stars/{self.user}/lists/{_list}')
    
    token = self.__search_before_text(r.text, self.CSRF_TOKEN_PATTERN, '<button type="submit" data-view-component="true" class="btn-danger btn">')
    assert token is not None, f"Can get token, list {_list} doesn't exist"

    data = {
      "_method": "delete",
      "authenticity_token": token
    }

    r = self.__post(f'/stars/{self.user}/lists/{_list}', data=data)
    assert r.status_code == 200, f"Failed, please check your cookies again {self.cookies}"
