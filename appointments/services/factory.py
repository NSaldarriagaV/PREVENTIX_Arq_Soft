from .strategies.specialty_default import DefaultSpecialtyOrderStrategy
from .strategies.base import ISpecialtyOrderStrategy


def build_specialty_strategy(name: str | None = None) -> ISpecialtyOrderStrategy:
    """
    Selecciona la estrategia de orden de especialidades.
    En el futuro puedes usar `name` para retornar variantes.
    """
    return DefaultSpecialtyOrderStrategy()
