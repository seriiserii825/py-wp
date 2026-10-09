from rich import print
from classes.pages.Page import Page
from classes.pages.RankMathMetabox import RankMathMetabox
from main_menu.post_menu import post_menu
from classes.utils.ColorMenu import ColorMenu


def page_menu():
    options = ["[green]Pages", "[blue]Posts"]
    choice = ColorMenu.select(options)
    if choice == 0:
        pages_menu()
    elif choice == 1:
        post_menu()
    else:
        print("[red]Exiting the program. Goodbye!")


def pages_menu():
    Page.list_all()

    menu_items = [
        "[green]List Pages",
        "[blue]Create One Page",
        "[blue]Create Multiple Pages",
        "[red]Delete One Page",
        "[red]Delete Multiple Pages",
        "[yellow]Ignore page",
        "[blue]Rename Page",
        "[blue]Change Template",
        "[blue]Set Front Page",
        "[blue]Toggle Rank Math metabox",
        "[yellow]Ignore page & Exit",
    ]

    choice = ColorMenu.select(menu_items, title="Page Menu")

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
