"""
Tests for :class:`CompareModelObjectsMixin`.

The model-related tests use ``Group``, ``Permission`` and ``ContentType`` from
``django.contrib.auth`` / ``django.contrib.contenttypes``. They cover a foreign
key (``Permission.content_type``), a many-to-many field (``Group.permissions``)
and a reverse relation (``Permission.group_set``) without needing dedicated
test models.

Failure messages are checked only for the reported paths (e.g. ``$.a.b``),
not for their wording, so the tests stay valid if the messages are translated.
"""

from collections import OrderedDict
from collections.abc import Mapping
from unittest.mock import ANY

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase, TestCase

from app_api.base.tests import CompareModelObjectsMixin


class ReturnList(list):
    """Stand-in for DRF's ``ReturnList`` (a ``list`` subclass)."""


class ReadOnlyMapping(Mapping):
    """A mapping that is neither a ``dict`` nor a ``dict`` subclass."""

    def __init__(self, **data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


class FailureAssertionsMixin:
    """Helper for asserting that a partial match fails at specific paths."""

    def assertMismatchAt(self, assertion, *, actual, expected, paths):
        """
        Assert that ``assertion`` fails and its message mentions every path.

        :param assertion: The bound assertion method under test.
        :param actual: Passed through as ``actual``.
        :param expected: Passed through as ``expected``.
        :param paths: Paths that must appear in the failure message.
        :return: The failure message, for further checks.
        """
        with self.assertRaises(AssertionError) as cm:
            assertion(actual=actual, expected=expected)
        message = str(cm.exception)
        for path in paths:
            self.assertIn(path, message)
        return message


class AssertModelObjectEqualsMappingTests(FailureAssertionsMixin, CompareModelObjectsMixin, SimpleTestCase):
    """Comparisons of mappings and scalar values."""

    def test_identical_dicts_pass(self):
        self.assertModelObjectEquals(actual={"a": 1, "b": 2}, expected={"a": 1, "b": 2})

    def test_extra_keys_in_actual_are_ignored(self):
        self.assertModelObjectEquals(
            actual={"a": 1, "created_at": "2026-01-01", "updated_at": "2026-01-02"},
            expected={"a": 1},
        )

    def test_empty_expected_matches_any_mapping(self):
        self.assertModelObjectEquals(actual={"a": 1}, expected={})

    def test_missing_key_in_actual_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"a": 1},
            expected={"a": 1, "b": 2},
            paths=["$.b"],
        )

    def test_comparison_is_asymmetric(self):
        # passes in one direction ...
        self.assertModelObjectEquals(actual={"a": 1, "b": 2}, expected={"a": 1})
        # ... but not in the other
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"a": 1},
            expected={"a": 1, "b": 2},
            paths=["$.b"],
        )

    def test_different_value_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"a": 1, "b": 3},
            expected={"a": 1, "b": 2},
            paths=["$.b"],
        )

    def test_none_values_are_compared(self):
        self.assertModelObjectEquals(actual={"a": None}, expected={"a": None})
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"a": None},
            expected={"a": 0},
            paths=["$.a"],
        )

    def test_nested_dict_is_compared_partially(self):
        self.assertModelObjectEquals(
            actual={"user": {"name": "Ada", "email": "ada@example.com"}},
            expected={"user": {"name": "Ada"}},
        )

    def test_nested_mismatch_reports_full_path(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"user": {"address": {"city": "Berlin"}}},
            expected={"user": {"address": {"city": "Hamburg"}}},
            paths=["$.user.address.city"],
        )

    def test_nested_ordered_dict_is_compared_partially(self):
        self.assertModelObjectEquals(
            actual={"x": OrderedDict(a=1, b=2)},
            expected={"x": OrderedDict(a=1)},
        )

    def test_custom_mapping_is_supported(self):
        self.assertModelObjectEquals(
            actual=ReadOnlyMapping(a=1, b=2),
            expected=ReadOnlyMapping(a=1),
        )

    def test_all_mismatches_are_reported_at_once(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"a": 1, "x": {"b": [1, {"c": 5}]}},
            expected={"a": 2, "x": {"b": [1, {"c": 2}]}, "m": 1},
            paths=["$.a", "$.x.b[1].c", "$.m"],
        )

    def test_any_matches_every_value(self):
        self.assertModelObjectEquals(
            actual={"id": 42, "token": "abc"},
            expected={"id": ANY, "token": ANY},
        )

    def test_any_still_requires_the_key(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"name": "Ada"},
            expected={"id": ANY},
            paths=["$.id"],
        )

    def test_mapping_expected_but_scalar_given_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"user": "Ada"},
            expected={"user": {"name": "Ada"}},
            paths=["$.user"],
        )

    def test_mapping_expected_but_none_given_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"user": None},
            expected={"user": {"name": "Ada"}},
            paths=["$.user"],
        )

    def test_scalars_are_compared_by_equality(self):
        self.assertModelObjectEquals(actual=1, expected=1)
        self.assertModelObjectEquals(actual="abc", expected="abc")
        self.assertMismatchAt(self.assertModelObjectEquals, actual=1, expected=2, paths=["$"])

    def test_strings_are_not_treated_as_sequences(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"tags": "ab"},
            expected={"tags": ["a", "b"]},
            paths=["$.tags"],
        )


class AssertModelObjectsListEqualTests(FailureAssertionsMixin, CompareModelObjectsMixin, SimpleTestCase):
    """Comparisons of sequences without database access."""

    def test_items_are_compared_partially(self):
        self.assertModelObjectsListEqual(
            actual=[{"a": 1, "b": 2}, {"a": 2, "b": 3}],
            expected=[{"a": 1}, {"a": 2}],
        )

    def test_empty_lists_pass(self):
        self.assertModelObjectsListEqual(actual=[], expected=[])

    def test_different_length_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectsListEqual,
            actual=[{"a": 1}],
            expected=[{"a": 1}, {"a": 2}],
            paths=["$"],
        )

    def test_order_matters(self):
        self.assertMismatchAt(
            self.assertModelObjectsListEqual,
            actual=[{"a": 2}, {"a": 1}],
            expected=[{"a": 1}, {"a": 2}],
            paths=["$[0].a", "$[1].a"],
        )

    def test_mismatching_item_reports_index(self):
        self.assertMismatchAt(
            self.assertModelObjectsListEqual,
            actual=[{"a": 1}, {"a": 3}],
            expected=[{"a": 1}, {"a": 2}],
            paths=["$[1].a"],
        )

    def test_missing_key_in_item_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectsListEqual,
            actual=[{"a": 1}, {"b": 1}],
            expected=[{"a": 1}, {"a": 2}],
            paths=["$[1].a"],
        )

    def test_list_of_scalars(self):
        self.assertModelObjectsListEqual(actual=[1, "x", None], expected=[1, "x", None])

    def test_nested_lists(self):
        self.assertModelObjectsListEqual(
            actual=[[{"a": 1, "b": 2}], [{"a": 2}]],
            expected=[[{"a": 1}], [{"a": 2}]],
        )

    def test_nested_list_mismatch_reports_full_path(self):
        self.assertMismatchAt(
            self.assertModelObjectsListEqual,
            actual=[[{"a": 1}], [{"a": 3}]],
            expected=[[{"a": 1}], [{"a": 2}]],
            paths=["$[1][0].a"],
        )

    def test_tuple_and_list_are_interchangeable(self):
        self.assertModelObjectsListEqual(actual=({"a": 1},), expected=[{"a": 1}])

    def test_list_subclass_is_supported(self):
        self.assertModelObjectsListEqual(
            actual=[ReturnList([{"a": 1, "b": 2}])],
            expected=[[{"a": 1}]],
        )

    def test_list_inside_dict(self):
        self.assertModelObjectEquals(
            actual={"items": [{"id": 1, "name": "x"}]},
            expected={"items": [{"id": 1}]},
        )

    def test_sequence_expected_but_mapping_given_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual={"items": {"id": 1}},
            expected={"items": [{"id": 1}]},
            paths=["$.items"],
        )


class AssertListContainsTests(CompareModelObjectsMixin, SimpleTestCase):
    """Tests for :meth:`CompareModelObjectsMixin.assertListContains`."""

    def test_subset_passes(self):
        self.assertListContains(actual=[1, 2, 3], expected=[1, 2])

    def test_order_is_ignored(self):
        self.assertListContains(actual=[3, 2, 1], expected=[1, 3])

    def test_empty_expected_passes(self):
        self.assertListContains(actual=[1], expected=[])

    def test_missing_items_fail_and_are_listed(self):
        with self.assertRaises(AssertionError) as cm:
            self.assertListContains(actual=[1, 2], expected=[1, 3, 4])
        message = str(cm.exception)
        self.assertIn("3", message)
        self.assertIn("4", message)

    def test_dict_items_are_compared_by_equality(self):
        self.assertListContains(actual=[{"a": 1}, {"b": 2}], expected=[{"b": 2}])
        with self.assertRaises(AssertionError):
            # no partial matching here, items must be equal
            self.assertListContains(actual=[{"a": 1, "b": 2}], expected=[{"a": 1}])


class KeywordOnlyArgumentsTests(CompareModelObjectsMixin, SimpleTestCase):
    """All public assertions must reject positional arguments."""

    def test_positional_arguments_are_rejected(self):
        for name in (
            "assertListContains",
            "assertModelObjectsListEqual",
            "assertModelObjectEquals",
            "assertPartialMatch",
        ):
            with self.subTest(assertion=name), self.assertRaises(TypeError):
                getattr(self, name)([1], [1])


class ModelComparisonTests(FailureAssertionsMixin, CompareModelObjectsMixin, TestCase):
    """Comparisons involving model instances, relations and querysets."""

    @classmethod
    def setUpTestData(cls):
        cls.content_type = ContentType.objects.get_for_model(Group)
        cls.can_fly = Permission.objects.create(name="Can fly", codename="can_fly", content_type=cls.content_type)
        cls.can_swim = Permission.objects.create(name="Can swim", codename="can_swim", content_type=cls.content_type)
        cls.pilots = Group.objects.create(name="pilots")
        cls.swimmers = Group.objects.create(name="swimmers")
        cls.pilots.permissions.add(cls.can_fly, cls.can_swim)
        cls.swimmers.permissions.add(cls.can_swim)

    def test_model_fields_are_compared_partially(self):
        self.assertModelObjectEquals(
            actual=self.can_fly,
            expected={"codename": "can_fly", "name": "Can fly"},
        )

    def test_model_field_mismatch_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual=self.can_fly,
            expected={"codename": "can_swim"},
            paths=["$.codename"],
        )

    def test_unknown_attribute_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual=self.can_fly,
            expected={"does_not_exist": 1},
            paths=["$.does_not_exist"],
        )

    def test_foreign_key_as_nested_structure(self):
        self.assertModelObjectEquals(
            actual=self.can_fly,
            expected={"content_type": {"app_label": "auth", "model": "group"}},
        )

    def test_foreign_key_mismatch_reports_nested_path(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual=self.can_fly,
            expected={"content_type": {"model": "user"}},
            paths=["$.content_type.model"],
        )

    def test_foreign_key_by_id(self):
        self.assertModelObjectEquals(
            actual=self.can_fly,
            expected={"content_type_id": self.content_type.pk},
        )

    def test_foreign_key_by_instance(self):
        self.assertModelObjectEquals(
            actual=self.can_fly,
            expected={"content_type": self.content_type},
        )

    def test_many_to_many_field(self):
        self.assertModelObjectEquals(
            actual=self.pilots,
            expected={"permissions": [{"codename": "can_fly"}, {"codename": "can_swim"}]},
        )

    def test_many_to_many_length_mismatch_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual=self.swimmers,
            expected={"permissions": [{"codename": "can_fly"}, {"codename": "can_swim"}]},
            paths=["$.permissions"],
        )

    def test_reverse_relation(self):
        self.assertModelObjectEquals(
            actual=self.can_fly,
            expected={"group_set": [{"name": "pilots"}]},
        )

    def test_model_instance_as_expected_is_compared_by_pk(self):
        self.assertModelObjectEquals(
            actual=Permission.objects.get(pk=self.can_fly.pk),
            expected=Permission.objects.get(pk=self.can_fly.pk),
        )
        self.assertMismatchAt(
            self.assertModelObjectEquals,
            actual=self.can_fly,
            expected=self.can_swim,
            paths=["$"],
        )

    def test_queryset_as_actual(self):
        self.assertModelObjectsListEqual(
            actual=Group.objects.order_by("name"),
            expected=[{"name": "pilots", "id": ANY}, {"name": "swimmers", "id": ANY}],
        )

    def test_queryset_order_matters(self):
        self.assertMismatchAt(
            self.assertModelObjectsListEqual,
            actual=Group.objects.order_by("-name"),
            expected=[{"name": "pilots"}, {"name": "swimmers"}],
            paths=["$[0].name", "$[1].name"],
        )

    def test_empty_queryset(self):
        self.assertModelObjectsListEqual(actual=Group.objects.none(), expected=[])

    def test_queryset_length_mismatch_fails(self):
        self.assertMismatchAt(
            self.assertModelObjectsListEqual,
            actual=Group.objects.filter(name="pilots"),
            expected=[{"name": "pilots"}, {"name": "swimmers"}],
            paths=["$"],
        )

    def test_values_queryset(self):
        self.assertModelObjectsListEqual(
            actual=Group.objects.order_by("name").values("id", "name"),
            expected=[{"name": "pilots"}, {"name": "swimmers"}],
        )

    def test_deeply_nested_relations(self):
        self.assertModelObjectsListEqual(
            actual=Group.objects.order_by("name"),
            expected=[
                {
                    "name": "pilots",
                    "permissions": [
                        {"codename": "can_fly", "content_type": {"model": "group"}},
                        {"codename": "can_swim"},
                    ],
                },
                {"name": "swimmers", "permissions": [{"codename": "can_swim"}]},
            ],
        )
