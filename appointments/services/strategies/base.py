from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence, Mapping
from typing import List


class ISpecialtyOrderStrategy(ABC):
    """Contrato para estrategias de ordenamiento de especialidades."""

    @abstractmethod
    def order(
        self,
        all_specialties: Sequence[str],
        user_specialty_counts: Mapping[str, int],
    ) -> List[str]:
        """Retorna la lista de especialidades ordenada según la estrategia."""
        ...
