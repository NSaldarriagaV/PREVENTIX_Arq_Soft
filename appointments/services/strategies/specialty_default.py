from typing import Sequence, List, Mapping
from .base import ISpecialtyOrderStrategy


class DefaultSpecialtyOrderStrategy(ISpecialtyOrderStrategy):
    """
    Orden por defecto:
    1) Primero las especialidades más usadas por el usuario (desc).
    2) Después el resto en el orden del catálogo.
    """
    def order(
        self,
        all_specialties: Sequence[str],
        user_specialty_counts: Mapping[str, int],
    ) -> List[str]:
        frequent = sorted(
            (s for s in all_specialties if s in user_specialty_counts),
            key=lambda s: user_specialty_counts.get(s, 0),
            reverse=True,
        )
        others = [s for s in all_specialties if s not in user_specialty_counts]
        return frequent + others
