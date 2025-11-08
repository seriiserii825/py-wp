from classes.utils.Command import Command


class AcfBlock:
    @staticmethod
    def get_blocks() -> list[str]:
        command = """
            wp eval '
            foreach (WP_Block_Type_Registry::get_instance()->get_all_registered() as $name => $block) {
                if (str_starts_with($name, "acf/")) {
                    echo $name . PHP_EOL;
                }
            }
            '
        """
        output = Command.run(command)
        blocks = output.strip().split("\n")
        return blocks
