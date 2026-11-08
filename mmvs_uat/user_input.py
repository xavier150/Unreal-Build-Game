from typing import Any, Dict, Tuple
from . import config


class PlayerInput:
    def __init__(self) -> None:
        self.title: str = ""
        self.description: str = ""
        self.options: Dict[int, Tuple[Any, str]] = {}

    def set_title(self, new_title: str) -> None:
        self.title = new_title

    def set_input_description(self, new_description: str) -> None:
        self.description = new_description

    def add_option(self, key: int, option_result: Any, title: str) -> None:
        self.options[key] = (option_result, title)

    def add_number_option(self, option_result: Any, title: str) -> None:
        key = len(self.options) + 1
        self.options[key] = (option_result, title)

    def add_yes_no_options(self) -> None:
        self.add_option(1, True, "Yes")
        self.add_option(2, False, "No")

    def ask_player_input(self) -> Any:
        print(self.title)
        for key, (_, title) in self.options.items():
            print(f"[{key}] {title}")

        input_result = input(self.description)

        # Check if the result is a integer
        if input_result.strip().isdigit():
            config_choice = int(input_result.strip())
        else:
            print("Invalid choice. Please enter a number. Try again...")
            return self.ask_player_input()



        if config_choice in self.options:
            return self.options[config_choice][0]
        else:
            print("Invalid choice.")
            exit(1)


      


def get_build_config() -> str:
    """
    Ask the user to choose between Custom, AsBefore, or Presets.
    
    Returns:
        str: "Custom", "AsBefore", or preset_id
    """
    player_input = PlayerInput()
    
    # Add Custom option
    player_input.add_number_option("Custom", "⚙️  Custom (Configure everything)")
    player_input.add_number_option("AsBefore", "🔄 As Before (Load last configuration)")
    
    # Add presets from config
    for preset in config.available_config_presets_v2:
        player_input.add_number_option(preset.preset_id, preset.title)
    
    player_input.set_title("Choose build configuration:")
    player_input.set_input_description("Enter the corresponding number: ")
    
    result = player_input.ask_player_input()
    if isinstance(result, str):
        return result
    else:
        raise ValueError("Invalid build configuration selected. Please choose a valid option.")


