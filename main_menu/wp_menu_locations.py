from classes.utils.Menu import Menu
from classes.wp_menus.WpMenuLocations import WpMenuLocations
from main_menu.wp_menu_handler import wp_menu_handler


def wp_menu_locations():
    wp_menu = WpMenuLocations()
    options = [
        "0).List Locations",
        "01).Create Location",
        "02).Edit Location",
        "03).Delete Location",
        "04).Choose Location Slug",
        "05).Exit",
    ]

    while True:
        wp_menu.list_locations()
        choice = Menu.select_fzf(options)
        if choice == 0:
            wp_menu.list_locations()
        elif choice == 1:
            wp_menu.create_location()
        elif choice == 2:
            wp_menu.edit_location()
        elif choice == 3:
            wp_menu.delete_location()
        elif choice == 4:
            wp_menu.choose_location_slug()
            wp_menu_handler()
        elif choice == 5:
            break
