"""Short-code generator hierarchy.

Mirrors the WeatherProvider ABC pattern from the TDD weather lab:
  BaseShortCodeGenerator (ABC)  ←  enforces the interface
  SecureShortCodeGenerator      ←  production implementation (secrets module)

Any future generator (e.g. NanoIDGenerator, SequentialGenerator) only
needs to subclass BaseShortCodeGenerator and implement ``generate``.
"""

import logging
import secrets
import string
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseShortCodeGenerator(ABC):
    """Abstract base class defining the contract for short-code generators.

    Subclasses must implement ``generate``.  The base class intentionally
    contains no state so implementations are free to be stateless functions
    or stateful objects (e.g. with a counter or external RNG seed).
    """

    @abstractmethod
    def generate(self, length: int = 6) -> str:
        """Generate a unique short code of the given length.

        Args:
            length: Number of characters in the returned code. Defaults to 6.

        Returns:
            An alphanumeric string of exactly ``length`` characters.
        """

    def __call__(self, length: int = 6) -> str:
        """Allow instances to be used as callables, satisfying ShortCodeGenerator Protocol."""
        return self.generate(length)


class SecureShortCodeGenerator(BaseShortCodeGenerator):
    """Production short-code generator using ``secrets.choice``.

    Uses the cryptographically secure ``secrets`` module instead of
    ``random`` so generated codes are suitable as public-facing tokens.

    Args:
        alphabet: Character set to draw from. Defaults to ASCII letters + digits.

    Example::

        gen = SecureShortCodeGenerator()
        code = gen.generate()        # e.g. "aB3xYz"
        code = gen(length=8)         # callable interface
    """

    def __init__(self, alphabet: str = string.ascii_letters + string.digits) -> None:
        self._alphabet = alphabet

    def generate(self, length: int = 6) -> str:
        code = "".join(secrets.choice(self._alphabet) for _ in range(length))
        logger.debug("SecureShortCodeGenerator produced code=%r", code)
        return code


# Module-level default instance — used by the serializer unless overridden.
default_generator: BaseShortCodeGenerator = SecureShortCodeGenerator()
