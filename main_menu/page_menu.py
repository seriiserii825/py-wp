from classes.pages.Page import Page
from classes.utils.Menu import Menu


def page_menu():
    menu_header = ["Index", "Option"]
    menu_colors = {
        "1": "green",
        "2": "yellow",
        "3": "yellow",
        "4": "blue",
        "5": "blue",
        "6": "red",
        "7": "red",
    }
    menu_items = [
        ["1", "List Pages"],
        ["2", "Create One Page"],
        ["3", "Create Multiple Pages"],
        ["4", "Delete One Page"],
        ["5", "Delete Multiple Pages"],
        ["6", "Exit"],
    ]

    Menu.display(
        title="Page Menu",
        columns=menu_header,
        rows=menu_items,
        row_styles=menu_colors,
    )

    choice = Menu.choose_option()
    if choice == 1:
        print("Listing pages...")
        Page.list_pages()
        page_menu()
    elif choice == 2:
        print("Creating one page...")
        Page.create_one()
        page_menu()
    elif choice == 3:
        print("Creating multiple pages...")
        Page.create_multiple()
        page_menu()
    elif choice == 4:
        print("Deleting one page...")
        Page.delete_one()
        page_menu()
    elif choice == 5:
        print("Deleting multiple pages...")
        Page.delete_multiple()
        page_menu()
    elif choice == 6:
        print("Exiting the program. Goodbye!")
        exit(0)
    else:
        print("Invalid choice. Please try again.")
