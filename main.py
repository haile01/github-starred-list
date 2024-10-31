import requests
import re

HOST = "https://github.com"
USER = "haile01"
CSRF_TOKEN_PATTERN = r'<input type="hidden" name="authenticity_token" value="(.+?)" autocomplete="off" />'
REPO_ID_PATTERN = r'<input type="hidden" name="repository_id" value="([0-9]+)">'
COOKIE = """..."""

def parse_cookie(s):
  cookies = {}
  for c in s.split(';'):
    name, value = c.strip().split('=')
    cookies[name] = value

  return cookies

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.71 Safari/537.36",
    "Accept": "text/html, application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://github.com"
}

cookies = parse_cookie(COOKIE)

def request(method, *args, **kwargs):
  print(args, kwargs)
  if method == 'get':
    return requests.get(*args, **kwargs, cookies=cookies)
  else:
    return requests.post(*args, **kwargs, headers=headers, cookies=cookies)

def search_before_text(s, pattern, text):
  ind = s.find(text)
  if ind != -1:
    s = s[:ind]

  found = re.findall(pattern, s)
  if len(found) == 0:
    return None

  return found[-1]

def create_list(name, desc):
  r = request('get', f'{HOST}/{USER}?tab=stars')
  token = search_before_text(r.text, CSRF_TOKEN_PATTERN, "Create a list to organize your starred repositories.")
  assert token is not None, "Can get token"

  data = {
      "authenticity_token": token,
      "user_list[name]": name,
      "user_list[description]": desc
  }

  r = request('post', f'{HOST}/stars/{USER}/lists', data=data)
  assert r.status_code == 200, "Should be OK"

def get_list_mapping_and_token(repo):
  mapping = {}
  r = request('get', f'{HOST}/{repo}/lists')

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
  found = re.findall(CSRF_TOKEN_PATTERN, r.text)

  return mapping, found[0]

def get_repo_id(repo):
  r = request('get', f'{HOST}/{repo}/lists')
  found = re.findall(REPO_ID_PATTERN, r.text)
  assert len(found) > 0, "Repo doesn't exist"

  return found[0]

def repo_to_list(repo, _list, add=True):
  mapping, token = get_list_mapping_and_token(repo)
  assert _list in mapping, "List doesn't exist"

  list_id = mapping[_list]

  data = {
      "_method": "put",
      "authenticity_token": token,
      "repository_id": get_repo_id(repo),
      "context": "user_list_menu",
      "list_ids[]": list_id if add else ""
  }

  r = request('post', f'{HOST}/{repo}/lists', data=data)
  assert r.status_code == 200, "Should be OK"

def add_repo(repo, _list):
  repo_to_list(repo, _list)

def remove_repo(repo, _list):
  repo_to_list(repo, _list, add=False)

def delete_list(_list):
  r = request('get', f'{HOST}/stars/{USER}/lists/{_list}')
  token = search_before_text(r.text, CSRF_TOKEN_PATTERN, '<button type="submit" data-view-component="true" class="btn-danger btn">')
  assert token is not None, "Can get token"

  data = {
      "_method": "delete",
      "authenticity_token": token
  }

  r = request('post', f'{HOST}/stars/{USER}/lists/{_list}', data=data)
  assert r.status_code == 200, "Should be OK"
