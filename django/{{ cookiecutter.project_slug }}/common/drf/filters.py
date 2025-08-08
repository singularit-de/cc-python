from django.forms import Field
from django_filters import Filter, FilterSet, MultipleChoiceFilter
from django_filters.widgets import QueryArrayWidget


class MultipleValuesField(Field):
    widget = QueryArrayWidget


class MultipleValuesFilter(MultipleChoiceFilter):
    field_class = MultipleValuesField