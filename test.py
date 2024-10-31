from gh_list import ListHandler


# cookie:   
# _octo=<value>; 
# preferred_color_mode=<value>; 
# _device_id=<value>; 
# user_session=<value>; 
# __Host-user_session_same_site=<value>; 
# tz=<value>; 
# color_mode=<value>; 
# logged_in=<value>; 
# dotcom_user=<value>; 
# GHCC=<value>; 
# tz=<value>; 
# _gh_sess=<value>;

if __name__ == "__main__":
    username = "nhtlongcs"
    list_title = "📖 special double space  Chars 📖"
    list_description = "ahgihihiihihi"
    repo_name = "codeigniter4/shield"

    cookie = ""
    helper = ListHandler(username, cookie)
    helper.create_list(list_title, list_description)
    helper.add_repo(repo_name, list_title)
    helper.remove_repo(repo_name, list_title)
    helper.delete_list(list_title)