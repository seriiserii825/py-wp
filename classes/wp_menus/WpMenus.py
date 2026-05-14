from classes.utils.WPPaths import WPPaths


class WpMenus:
    def __init__(self):
        self.theme_path = WPPaths.get_theme_path()
        print(f'{self.theme_path}: self.theme_path')
        self.setup_file_path = self.theme_path / "inc/ar-setup.php"
        print(f'{self.setup_file_path}: self.setup_file_path')

    def list_menus(self):
        print("Menu functionality is not implemented yet.")
