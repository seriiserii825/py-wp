from rich import print
from classes.pages.Page import Page
from classes.pages.RankMathMetabox import RankMathMetabox
from main_menu.post_menu import post_menu
from main_menu.table_menu import table_menu


def page_menu():
    choice = table_menu("Pages / Posts", ["Pages", "Posts"])
    if choice == 0:
        pages_menu()
        page_menu()
    elif choice == 1:
        post_menu()
        page_menu()
    # Back → return to the main menu


def pages_menu():
    Page.list_all()

    options = [
        "List Pages",
        "Create One Page",
        "Create Multiple Pages",
        "Delete One Page",
        "Delete Multiple Pages",
        "Ignore page",
        "Rename Page",
        "Change Template",
        "Set Front Page",
        "Toggle Rank Math metabox",
        "Ignore page & Exit",
    ]
    choice = table_menu(
        "Page Menu",
        options,
        red_options={"Delete One Page", "Delete Multiple Pages"},
    )

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
        exit(0)
    # Back → return to Pages / Posts
