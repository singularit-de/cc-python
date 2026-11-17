from collections import OrderedDict
from typing import Union

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import QuerySet



_MISSING = object()
class CompareModelObjectsMixin:
    """
    Mixin for :class:`django.test.TestCase` (or :class:`unittest.TestCase`)
    that adds asymmetric partial-match assertions.

    Matching rules:

    * **Mappings** (``dict``, ``OrderedDict``, DRF ``ReturnDict``, ...): every key
      of ``expected`` must exist in ``actual`` and match recursively. Additional
      keys in ``actual`` are ignored.
    * **Model instances** as ``actual``: keys of ``expected`` are resolved via
      attribute access, so foreign keys, many-to-many fields, reverse relations
      and properties can be compared as nested structures.
    * **Sequences** (``list``, ``tuple``, :class:`~django.db.models.QuerySet`,
      related managers, ...): must have the same length and are compared
      position by position.
    * **Everything else** is compared with ``!=``. Model instances in
      ``expected`` are therefore compared by primary key.

    Use :data:`unittest.mock.ANY` as a value to assert that a key is present
    without checking its value.

    All assertions accept keyword arguments only, so ``actual`` and
    ``expected`` cannot be swapped by accident.

    .. note::
        Sequence comparison is order-sensitive. Querysets without
        :meth:`~django.db.models.query.QuerySet.order_by` have no guaranteed
        order and can lead to flaky tests.

    .. note::
        Attribute access on relations may trigger database queries.
    """

    def assertListContains(self, *, actual: Sequence, expected: Sequence) -> None:
        """
        Assert that every item of ``expected`` is contained in ``actual``.

        Items are compared with ``in``, i.e. by equality. Order and additional
        items in ``actual`` are ignored.

        :param actual: The actual sequence.
        :param expected: The items that must be present in ``actual``.
        :raises AssertionError: If at least one item of ``expected`` is missing
            in ``actual``. The message lists all missing items.

        Example:

        .. code-block:: python

            self.assertListContains(actual=[1, 2, 3], expected=[1, 2])  # passes
            self.assertListContains(actual=[1, 2], expected=[1, 2, 3])  # fails
        """
        missing = [item for item in expected if item not in actual]
        if missing:
            self.fail(f"Missing items: {missing!r}\nActual: {actual!r}")

    def assertModelObjectsListEqual(self, *, actual: Sequence | QuerySet, expected: Sequence) -> None:
        """
        Assert that a sequence of objects partially matches ``expected``.

        Both sequences must have the same length. Items are compared position
        by position using the rules described in
        :class:`CompareModelObjectsMixin`.

        :param actual: The actual sequence, e.g. a list of dicts from an API
            response or a :class:`~django.db.models.QuerySet`.
        :param expected: The expected sequence. Only keys present in its items
            are checked.
        :raises AssertionError: If the lengths differ or any item does not
            match. The message lists all mismatches with their path.

        Example:

        .. code-block:: python

            self.assertModelObjectsListEqual(
                actual=Book.objects.order_by("id"),
                expected=[{"title": "Dune", "id": ANY}, {"title": "Emma", "id": ANY}],
            )
        """
        self.assertPartialMatch(actual=actual, expected=expected)

    def assertModelObjectEquals(self, *, actual: Any, expected: Any) -> None:
        """
        Assert that a single object partially matches ``expected``.

        Typical use is excluding fields such as ``created_at`` or
        ``updated_at`` simply by leaving them out of ``expected``.

        :param actual: The actual object: a mapping, a model instance or any
            other object.
        :param expected: The expected structure. Only keys present here are
            checked.
        :raises AssertionError: If a key of ``expected`` is missing in
            ``actual`` or a value does not match. The message lists all
            mismatches with their path.

        Example:

        .. code-block:: python

            # passes: "b" is not part of expected and therefore ignored
            self.assertModelObjectEquals(actual={"a": 1, "b": 2}, expected={"a": 1})

            # fails: "b" is expected but missing in actual
            self.assertModelObjectEquals(actual={"a": 1}, expected={"a": 1, "b": 2})

            # nested relations on a model instance
            self.assertModelObjectEquals(
                actual=book,
                expected={"title": "Dune", "author": {"name": "Frank Herbert"}},
            )
        """
        self.assertPartialMatch(actual=actual, expected=expected)

    def assertPartialMatch(self, *, actual: Any, expected: Any) -> None:
        """
        Assert that ``actual`` partially matches ``expected``.

        Generic entry point used by :meth:`assertModelObjectEquals` and
        :meth:`assertModelObjectsListEqual`. Accepts single objects as well as
        sequences. All mismatches are collected before failing, so a single
        test run shows every difference.

        :param actual: The actual value.
        :param expected: The expected value or structure.
        :raises AssertionError: If any mismatch is found. Each mismatch is
            reported with a path such as ``$.author.books[1].title``.
        """
        errors: list[str] = []
        self._collect_mismatches(actual, expected, "$", errors)
        if errors:
            self.fail("Partial match failed:\n  " + "\n  ".join(errors))

    @staticmethod
    def _is_sequence(obj: Any) -> bool:
        """
        Return whether ``obj`` is compared as a sequence.

        Strings and bytes are excluded on purpose, as they are compared as
        scalar values.

        :param obj: The object to check.
        :return: ``True`` for sequences, querysets and related managers.
        """
        if isinstance(obj, (str, bytes, bytearray)):
            return False
        return isinstance(obj, (Sequence, QuerySet, BaseManager))

    @staticmethod
    def _lookup(obj: Any, key: str) -> Any:
        """
        Look up ``key`` in ``obj``.

        Mappings are accessed by key, all other objects by attribute. Using
        attribute access instead of ``__dict__`` makes foreign keys,
        many-to-many fields, reverse relations and properties available on
        model instances.

        :param obj: A mapping or any other object.
        :param key: The key or attribute name.
        :return: The value, or the ``_MISSING`` sentinel if it does not exist.
        """
        if isinstance(obj, Mapping):
            return obj.get(key, _MISSING)
        return getattr(obj, key, _MISSING)

    def _collect_mismatches(self, actual: Any, expected: Any, path: str, errors: list[str]) -> None:
        """
        Recursively compare ``actual`` with ``expected`` and collect mismatches.

        :param actual: The actual value at the current path.
        :param expected: The expected value at the current path.
        :param path: The current path, used in error messages (root is ``$``).
        :param errors: List that mismatch descriptions are appended to.
        """
        if isinstance(expected, Mapping):
            if not isinstance(actual, (Mapping, models.Model)):
                errors.append(f"{path}: expected mapping or model, got {type(actual).__name__}: {actual!r}")
                return
            for key, exp_value in expected.items():
                act_value = self._lookup(actual, key)
                if act_value is _MISSING:
                    errors.append(f"{path}.{key}: missing key")
                else:
                    self._collect_mismatches(act_value, exp_value, f"{path}.{key}", errors)
            return

        if self._is_sequence(expected):
            if isinstance(actual, BaseManager):  # e.g. book.tags
                actual = actual.all()
            if not self._is_sequence(actual):
                errors.append(f"{path}: expected sequence, got {type(actual).__name__}: {actual!r}")
                return
            actual, expected = list(actual), list(expected)
            if len(actual) != len(expected):
                errors.append(f"{path}: length {len(actual)}, expected {len(expected)}")
                return
            for i, (act_item, exp_item) in enumerate(zip(actual, expected)):
                self._collect_mismatches(act_item, exp_item, f"{path}[{i}]", errors)
            return

        if actual != expected:
            errors.append(f"{path}: {actual!r} != expected {expected!r}")


