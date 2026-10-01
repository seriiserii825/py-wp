from rich import print
from classes.pages.RankMathMetabox import RankMathMetabox
from classes.posts.Post import Post
from py_libs.Menu import Menu


def post_menu():
    Post.list_all()

    menu_header = ["Index", "Option"]
    menu_colors = {
        0: "green",
        1: "blue",
        2: "blue",
        3: "red",
        4: "blue",
        5: "blue",
        6: "red",
    }
    menu_items = [
        ["0", "List Posts"],
        ["1", "Create One Post"],
        ["2", "Create Multiple Posts"],
        ["3", "Delete Posts"],
        ["4", "Rename Post"],
        ["5", "Toggle Rank Math metabox"],
        ["6", "Exit"],
    ]

    Menu.display(
        title="Post Menu",
        columns=menu_header,
        rows=menu_items,
        row_styles=menu_colors,
    )

    choice = Menu.choose_option()

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
