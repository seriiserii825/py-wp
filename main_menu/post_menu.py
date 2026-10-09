from rich import print
from classes.pages.RankMathMetabox import RankMathMetabox
from classes.posts.Post import Post
from classes.utils.ColorMenu import ColorMenu


def post_menu():
    Post.list_all()

    menu_items = [
        "[green]List Posts",
        "[blue]Create One Post",
        "[blue]Create Multiple Posts",
        "[red]Delete Posts",
        "[blue]Rename Post",
        "[blue]Toggle Rank Math metabox",
    ]

    choice = ColorMenu.select(menu_items, title="Post Menu")

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
    elif choice == 6:
        print("[red]Exiting the program. Goodbye!")
        return
    else:
        print("[red]Invalid choice. Please try again.")
        return
