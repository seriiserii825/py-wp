from rich import print
from classes.pages.Page import Page
from classes.utils.Menu import Menu


def page_menu():
    Page.list_pages()

    menu_header = ["Index", "Option"]
    menu_colors = {
        0: "green",
        1: "yellow",
        2: "yellow",
        3: "blue",
        4: "blue",
        5: "red",
    }
    menu_items = [
        ["0", "List Pages"],
        ["1", "Create One Page"],
        ["2", "Create Multiple Pages"],
        ["3", "Delete One Page"],
        ["4", "Delete Multiple Pages"],
        ["5", "Exit"],
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
        Page.list_pages()
        page_menu()
    elif choice == 1:
        print("Creating one page...")
        Page.create_one()
        page_menu()
    elif choice == 2:
        print("Creating multiple pages...")
        Page.create_multiple()
        page_menu()
    elif choice == 3:
        print("Deleting one page...")
        Page.delete_one()
        Page.list_pages()
        page_menu()
    elif choice == 4:
        print("Deleting multiple pages...")
        Page.delete_multiple()
        page_menu()
    elif choice == 5:
        print("[red]Exiting the program. Goodbye!")
        return
    else:
        print("[red]Invalid choice. Please try again.")
        return
