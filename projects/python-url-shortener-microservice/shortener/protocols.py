"""Protocols for the shortener app.

Defines structural contracts (PEP 544) that components must satisfy.
Using Protocol instead of ABC here because generate_short_code is a
plain callable — any function or object with a matching signature
satisfies the contract without explicit inheritance.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ShortCodeGenerator(Protocol):
    """Structural contract for any short-code generator.

    Any callable that accepts an optional ``length: int`` and returns
    a ``str`` satisfies this protocol — no inheritance required.

    Example::

        def my_generator(length: int = 6) -> str:
            return "abc123"

        assert isinstance(my_generator, ShortCodeGenerator)  # True
    """

    def __call__(self, length: int = 6) -> str:
        """Generate and return a unique short code.

        Args:
            length: Desired length of the generated code.

        Returns:
            A unique alphanumeric string of ``length`` characters.
        """
        ...
