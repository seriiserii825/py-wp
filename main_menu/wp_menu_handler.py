from classes.wp_menus.WpMenu import WpMenu
from main_menu.table_menu import BACK, table_menu


def wp_menu_handler(location: str):
    wp_menu = WpMenu(location)

    if not wp_menu._get_menu_slug():
        wp_menu.create_and_assign()
        if not wp_menu._get_menu_slug():
            return

    options = [
        "Create Item",
        "Edit Item",
        "Move Item",
        "Delete Item",
    ]

    def render() -> list:
        return wp_menu.list_items()

    items = render()
    while True:
        choice = table_menu(f"Menu: {location}", options, red_options={"Delete Item"})
        if choice == 0:
            wp_menu.create_item(items)
            items = render()
        elif choice == 1:
            wp_menu.edit_item(items)
            items = render()
        elif choice == 2:
            wp_menu.move_item(items)
            items = render()
        elif choice == 3:
            wp_menu.delete_item(items)
            items = render()
        elif choice == BACK:
            break
