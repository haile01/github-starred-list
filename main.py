import requests
import re

class ListHelper:
  def __init__(self, user, cookie):
    self.HOST = "https://github.com"
    self.CSRF_TOKEN_PATTERN = r'<input type="hidden" name="authenticity_token" value="(.+?)" autocomplete="off" />'
    self.REPO_ID_PATTERN = r'<input type="hidden" name="repository_id" value="([0-9]+)">'

    self.user = user
    self.__get, self.__post = self.__init_requests(cookie)

  def __parse_cookie(self, s):
    cookies = {}
    for c in s.split(';'):
      name, value = c.strip().split('=')
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

    cookies = self.__parse_cookie(cookie)

    def get(path, *args, **kwargs):
      print('get', args, kwargs)
      return requests.get(self.HOST + path, *args, **kwargs, cookies=cookies)

    def post(path, *args, **kwargs):
      print('post', args, kwargs)
      return requests.post(self.HOST + path, *args, **kwargs, headers=headers, cookies=cookies)

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
    assert r.status_code == 200, "Should be OK"

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
    assert r.status_code == 200, "Should be OK"

  def add_repo(self, repo, _list):
    self.__repo_to_list(repo, _list)

  def remove_repo(self, repo, _list):
    self.__repo_to_list(repo, _list, add=False)

  def delete_list(self, _list):
    r = self.__get(f'/stars/{self.user}/lists/{_list}')
    token = self.__search_before_text(r.text, self.CSRF_TOKEN_PATTERN, '<button type="submit" data-view-component="true" class="btn-danger btn">')
    assert token is not None, "Can get token"

    data = {
      "_method": "delete",
      "authenticity_token": token
    }

    r = self.__post(f'/stars/{self.user}/lists/{_list}', data=data)
    assert r.status_code == 200, "Should be OK"

if __name__ == "__main__":
  cookie = """..."""
  helper = ListHelper("haile01", cookie)
  helper.create_list("test1234", "ahgihihiihihi")
  input()
  helper.add_repo("codeigniter4/shield", "test1234")
  input()
  helper.remove_repo("codeigniter4/shield", "test1234")
  input()
  helper.delete_list("test1234")
