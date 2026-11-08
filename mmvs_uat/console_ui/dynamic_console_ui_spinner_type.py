from typing import List
import time

class BaseDisplaySpinner:
    """Classe de base pour les spinners d'affichage."""
    def __init__(self, states: List[str], speed_seconds: float) -> None:
        self.__frame: int = 0
        self.states: List[str] = states
        self.speed_seconds: float = speed_seconds

    def update_spinner(self) -> None:
        """Met à jour la frame du spinner basée sur le temps écoulé."""
        self.__frame = int(time.time() / self.speed_seconds) % len(self.states)

    def get_current_state(self) -> str:
        """Retourne l'état courant du spinner."""
        return self.states[self.__frame]


class DisplaySpinnerUi(BaseDisplaySpinner):
    def __init__(self) -> None:
        spinner_chars: List[str] = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        super().__init__(states=spinner_chars, speed_seconds=0.1)

    def get_current_spinner_char(self) -> str:
        return self.get_current_state()


class DisplayDotSpinnerUi(BaseDisplaySpinner):
    def __init__(self) -> None:
        dot_states: List[str] = ['.  ', '.. ', '...']
        super().__init__(states=dot_states, speed_seconds=0.5)

    def get_current_dot_state(self) -> str:
        return self.get_current_state()