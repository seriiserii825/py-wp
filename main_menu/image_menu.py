from classes.images.ImageClass import ImagesClass
from classes.utils.ColorMenu import ColorMenu


def image_menu():
    image_class = ImagesClass()
    image_class.replace_space_with_uderscore()
    image_class.show_downloads_images()
    choice = ColorMenu.select([
        "[green]Show all",
        "[green]Upload all",
        "[blue]Select",
        "[red]Delete images by select",
    ])
    if choice == 0:
        image_class.show_images_with_sizes_json()
        image_menu()
    elif choice == 1:
        image_class.upload_all()
        image_class.show_images_with_sizes_json()
        image_menu()
    elif choice == 2:
        image_class.select_images()
        image_class.show_images_with_sizes_json()
        image_menu()
    elif choice == 3:
        image_class.delete_image()
        image_class.show_images_with_sizes_json()
        image_menu()
    else:
        exit("Goodbye!")
