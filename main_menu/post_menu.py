from rich import print
from classes.pages.RankMathMetabox import RankMathMetabox
from classes.posts.Post import Post
from main_menu.table_menu import table_menu


def post_menu():
    Post.list_all()

    options = [
        "List Posts",
        "Create One Post",
        "Create Multiple Posts",
        "Delete Posts",
        "Rename Post",
        "Toggle Rank Math metabox",
    ]
    choice = table_menu("Post Menu", options, red_options={"Delete Posts"})

    if choice == 0:
        Post.list_all()
        post_menu()
    elif choice == 1:
        print("Creating one post...")
        Post.create_one()
        post_menu()
    elif choice == 2:
        print("Creating multiple posts...")
        Post.create_many()
        post_menu()
    elif choice == 3:
        print("Deleting posts...")
        Post.delete()
        post_menu()
    elif choice == 4:
        print("Renaming post...")
        Post.rename()
        post_menu()
    elif choice == 5:
        RankMathMetabox.toggle(post_type="post")
        post_menu()
    # Back → return one level up
