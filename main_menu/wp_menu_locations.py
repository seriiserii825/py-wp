from classes.wp_menus.WpMenuLocations import WpMenuLocations
from main_menu.table_menu import BACK, table_menu
from main_menu.wp_menu_handler import wp_menu_handler


def wp_menu_locations():
    wp_menu = WpMenuLocations()
    if not wp_menu.file_exists:
        wp_menu.show_missing_hint()
        return
    options = [
        "Choose Location Slug",
        "List Locations",
        "Create Location",
        "Edit Location",
        "Delete Location",
    ]

    while True:
        wp_menu.list_locations()
        choice = table_menu("Menus", options, red_options={"Delete Location"})
        if choice == 0:
            location_slug = wp_menu.choose_location_slug()
            if location_slug:
                wp_menu_handler(location_slug)
        elif choice == 1:
            wp_menu.list_locations()
        elif choice == 2:
            wp_menu.create_location()
        elif choice == 3:
            wp_menu.edit_location()
        elif choice == 4:
            wp_menu.delete_location()
        elif choice == BACK:
            break
