from classes.utils.Menu import Menu
from classes.wp_menus.WpMenu import WpMenu


def wp_menu_handler(location: str):
    wp_menu = WpMenu(location)

    if not wp_menu._get_menu_slug():
        wp_menu.create_and_assign()
        if not wp_menu._get_menu_slug():
            return

    options = [
        "0.Create Item",
        "1.Edit Item",
        "2.Move Item",
        "3.Delete Item",
        "4.Exit",
    ]

    def render() -> list:
        return wp_menu.list_items()

    items = render()
    while True:
        choice = Menu.select_fzf(options)
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
        elif choice == 4:
            break
