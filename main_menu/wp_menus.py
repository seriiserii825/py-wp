from classes.utils.Menu import Menu


def wp_menus():
    options = [
        "0).List Menus",
        "01).Add Menu",
        "02).Edit Menu",
        "03).Delete Menu",
        "04).Choose Menu Location",
        "05).Exit",
    ]
    choice = Menu.select_fzf(options)
    if choice == 0:
        print("Menu functionality is not implemented yet.")
        wp_menus()
    elif choice == 1:
        exit(0)
