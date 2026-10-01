from rich import print
from classes.pages.Page import Page
from classes.pages.RankMathMetabox import RankMathMetabox
from main_menu.post_menu import post_menu
from py_libs.Menu import Menu


def page_menu():
    options = ["0).Pages", "1).Posts", "2).Exit"]
    choice = Menu.select_fzf(options)
    if choice == 0:
        pages_menu()
    elif choice == 1:
        post_menu()
    else:
        print("[red]Exiting the program. Goodbye!")


def pages_menu():
    Page.list_all()

    menu_header = ["Index", "Option"]
    menu_colors = {
        0: "green",
        1: "blue",
        2: "blue",
        3: "red",
        4: "red",
        5: "yellow",
        6: "blue",
        7: "blue",
        8: "blue",
        9: "blue",
        10: "yellow",
        11: "red",
    }
    menu_items = [
        ["0", "List Pages"],
        ["1", "Create One Page"],
        ["2", "Create Multiple Pages"],
        ["3", "Delete One Page"],
        ["4", "Delete Multiple Pages"],
        ["5", "Ignore page"],
        ["6", "Rename Page"],
        ["7", "Change Template"],
        ["8", "Set Front Page"],
        ["9", "Toggle Rank Math metabox"],
        ["10", "Ignore page & Exit"],
        ["11", "Exit"],
    ]

    Menu.display(
        title="Page Menu",
        columns=menu_header,
        rows=menu_items,
        row_styles=menu_colors,
    )

    choice = Menu.choose_option()

    if choice == 0:
        print("Listing pages...")
        Page.list_all()
        pages_menu()
    elif choice == 1:
        print("Creating one page...")
        Page.create_one()
        pages_menu()
    elif choice == 2:
        print("Creating multiple pages...")
        Page.create_many()
        pages_menu()
    elif choice == 3:
        print("Deleting one page...")
        Page.delete()
        Page.list_all()
        pages_menu()
    elif choice == 4:
        print("Deleting multiple pages...")
        Page.delete_multiple()
        pages_menu()
    elif choice == 5:
        print("[yellow]Ignoring page operation. Returning to main menu.")
        Page.ignore_page()
        pages_menu()
    elif choice == 6:
        print("Renaming page...")
        Page.rename()
        pages_menu()
    elif choice == 7:
        print("Changing page template...")
        Page.change_template()
        pages_menu()
    elif choice == 8:
        print("Setting front page...")
        Page.set_front_page()
        pages_menu()
    elif choice == 9:
        RankMathMetabox.toggle()
        pages_menu()
    elif choice == 10:
        Page.ignore_page()
        return
    elif choice == 11:
        print("[red]Exiting the program. Goodbye!")
        return
    else:
        print("[red]Invalid choice. Please try again.")
        return
