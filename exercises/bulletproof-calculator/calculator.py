"""Division utility for a financial application."""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def divide_funds(total: float, parts: float) -> float:
    """Divide a total amount into equal parts.

    Args:
        total: The total amount to divide.
        parts: The number of parts to divide into.

    Returns:
        The result of dividing total by parts.

    Raises:
        ZeroDivisionError: If parts is zero.
        TypeError: If either argument is not a number.
    """
    try:
        result = total / parts
        logger.info("divide_funds(%s, %s) = %s", total, parts, result)
        return result
    except ZeroDivisionError:
        logger.error("Division by zero: parts=%s", parts, exc_info=True)
        raise
    except TypeError:
        logger.error(
            "Invalid types: total=%s (%s), parts=%s (%s)",
            total,
            type(total).__name__,
            parts,
            type(parts).__name__,
            exc_info=True,
        )
        raise
