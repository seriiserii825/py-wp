import os

from dataclasses import dataclass
from rich import print

from classes.utils.Command import Command
from classes.utils.Menu import Menu
from classes.utils.Select import Select


@dataclass
class ImageDto:
    id: int
    post_title: str
    post_date: str


class ImagesClass:
    def __init__(self):
        self.downloads_dir = os.path.expanduser("~") + "/Downloads"
        self.have_images_in_downloads()
        self.replace_space_with_uderscore()

    def show_images(self):
        headers = ["ID", "Title", "Date"]
        rows = []
        images = self._get_installed_images()
        for image in images:
            rows.append([str(image.id), image.post_title, image.post_date])
        Menu.display(
            "Images",
            headers,
            rows,
        )

    def _get_installed_images(self) -> list[ImageDto]:
        images_from_command = Command.run_json(
            "wp post list --post_type=attachment --format=json"
        )
        images: list[ImageDto] = []

        if not isinstance(images_from_command, list):
            print("Invalid image data:", images_from_command)
        else:
            # Преобразуем каждый dict в ImageDto
            images = [
                ImageDto(
                    id=img["ID"],
                    post_title=img["post_title"],
                    post_date=img["post_date"],
                )
                for img in images_from_command
                if all(k in img for k in ("ID", "post_title", "post_date"))
            ]

        images.sort(key=lambda x: x.post_date, reverse=False)
        return images

    def delete_image(self):
        images = self._get_installed_images()
        images.sort(key=lambda x: x.post_date, reverse=True)
        all_images = [f"{img.id}-{img.post_title}" for img in images]
        selected_images = Select.select_with_fzf(all_images)
        image_ids = [img.split("-")[0] for img in selected_images]
        if not image_ids:
            print("[red]No images selected for deletion.")
            return
        print(f"[yellow]Deleting images with IDs: {', '.join(image_ids)}")
        agree = input("[yellow]Are you sure you want to delete these images? (y/n): ")
        if agree.lower() != "y":
            print("[red]Deletion cancelled.")
            return
        for image_id in image_ids:
            if image_id.isdigit():
                Command.run(f"wp post delete {image_id} --force")
        self.show_images()

    def have_images_in_downloads(self):
        files = os.listdir(self.downloads_dir)
        for item in files:
            if item.endswith(".jpg") or item.endswith(".png") or item.endswith(".svg"):
                return True
        print("[red]No images found in Downloads folder!")
        exit()

    def replace_space_with_uderscore(self):
        files = os.listdir(self.downloads_dir)
        for item in files:
            if item.endswith(".jpg") or item.endswith(".png") or item.endswith(".svg"):
                new_name = item.replace(" ", "_")
                new_name_path = os.path.join(self.downloads_dir, new_name)
                old_name_path = os.path.join(self.downloads_dir, item)
                os.rename(old_name_path, new_name_path)

    def get_images(self):
        images = []
        files = os.listdir(self.downloads_dir)
        for item in files:
            if item.endswith(".jpg") or item.endswith(".png") or item.endswith(".svg"):
                images.append(item)
        sorted_images = sorted(images)
        return sorted_images

    def optimize_image(self, image):
        os.system(
            f"jpegoptim --strip-all --all-progressive -ptm 80 ~/Downloads/{image}"
        )

    def upload_image(self, image: str):
        os.system("wp media import ~/Downloads/" + image + " --title=" + image)

    def upload_all(self):
        images = self.get_images()
        self.import_images(images)

    def select_images(self):
        images = self.get_images()
        selected_images = Select.select_multiple(images)
        self.import_images(selected_images)

    def import_images(self, images: list[str]):
        for image in images:
            if image.endswith(".jpg"):
                self.optimize_image(image)
                self.upload_image(image)
            elif image.endswith(".png"):
                convert_png = input(
                    'Do you want to convert "{image}" png to jpg, (y/n)? '
                )
                if convert_png == "y":
                    os.system("mogrify -format jpg ~/Downloads/" + image)
                    new_image = image.replace(".png", ".jpg")
                    os.system("rm ~/Downloads/" + image)
                    self.optimize_image(new_image)
                    self.upload_image(new_image)
                else:
                    self.upload_image(image)
            else:
                self.upload_image(image)
        self.show_images()
