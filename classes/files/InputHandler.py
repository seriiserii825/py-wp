from dto.FileConfig import FileConfig
from enum.FileTypeEnum import FileTypeEnum


class InputHandler:
    def __init__(self, file_type_enum: FileTypeEnum):
        self.file_type_enum = file_type_enum

    def get_user_choice(self) -> FileConfig:
        filename = input("Enter the file name (without extension): ").strip()
        folder = input("Enter the folder inside template-parts/: ").strip()

        generate_php = input("Generate PHP file? (y/n): ").lower().startswith("y")
        generate_scss = input("Generate SCSS file? (y/n): ").lower().startswith("y")
        scss_autoinject = False
        if generate_scss:
            scss_autoinject = (
                input("Inject into src/my.scss? (y/n): ").lower().startswith("y")
            )

        return FileConfig(
            filename=filename,
            folder=folder,
            generate_php=generate_php,
            generate_scss=generate_scss,
            scss_autoinject=scss_autoinject,
        )
