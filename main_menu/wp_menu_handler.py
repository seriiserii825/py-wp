from classes.utils.Menu import Menu
from classes.wp_menus.WpMenu import WpMenu


def wp_menu_handler(location: str):
    wp_menu = WpMenu(location)

    if not wp_menu._get_menu_slug():
        wp_menu.create_and_assign()
        if not wp_menu._get_menu_slug():
            return

    options = [
        "0).List Items",
        "01).Create Item",
        "02).Edit Item",
        "03).Move Item",
        "04).Delete Item",
        "05).Exit",
    ]

    wp_menu.list_items()
    while True:
        choice = Menu.select_fzf(options)
        if choice == 0:
            wp_menu.list_items()
        elif choice == 1:
            wp_menu.create_item()
            wp_menu.list_items()
        elif choice == 2:
            wp_menu.edit_item()
            wp_menu.list_items()
        elif choice == 3:
            wp_menu.move_item()
            wp_menu.list_items()
        elif choice == 4:
            wp_menu.delete_item()
            wp_menu.list_items()
        elif choice == 5:
            break
