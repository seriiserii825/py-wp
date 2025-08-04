from classes.images.ImageClass import ImagesClass
from rich import print


def image_menu():
    image_class = ImagesClass()
    image_class.replace_space_with_uderscore()
    print("[green]1) Show all")
    print("[green]2) Upload all")
    print("[blue]3) Select")
    print("[red]4) Delete Image")
    print("[red]5) Exit")

    choice = input("Make your choice:")
    if choice == "1":
        image_class.show_images()
        image_menu()
    elif choice == "2":
        image_class.upload_all()
        image_menu()
    elif choice == "3":
        image_class.select_images()
        image_menu()
    elif choice == "4":
        image_class.delete_image()
        image_menu()
    elif choice == "5":
        exit("Goodbye!")
    else:
        exit("Goodbye!")
