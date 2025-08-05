from rich import print
from classes.pages.Page import Page
from classes.utils.Menu import Menu


def page_menu():
    Page.list_all()

    menu_header = ["Index", "Option"]
    menu_colors = {
        0: "green",
        1: "blue",
        2: "blue",
        3: "red",
        4: "red",
        5: "yellow",
        6: "red",
    }
    menu_items = [
        ["0", "List Pages"],
        ["1", "Create One Page"],
        ["2", "Create Multiple Pages"],
        ["3", "Delete One Page"],
        ["4", "Delete Multiple Pages"],
        ["5", "Ignore page"],
        ["6", "Exit"],
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
        page_menu()
    elif choice == 1:
        print("Creating one page...")
        Page.create_one()
        page_menu()
    elif choice == 2:
        print("Creating multiple pages...")
        Page.create_many()
        page_menu()
    elif choice == 3:
        print("Deleting one page...")
        Page.delete()
        Page.list_all()
        page_menu()
    elif choice == 4:
        print("Deleting multiple pages...")
        Page.delete_multiple()
        page_menu()
    elif choice == 5:
        print("[yellow]Ignoring page operation. Returning to main menu.")
        Page.ignore_page()
        page_menu()
    elif choice == 6:
        print("[red]Exiting the program. Goodbye!")
        return
    else:
        print("[red]Invalid choice. Please try again.")
        return
