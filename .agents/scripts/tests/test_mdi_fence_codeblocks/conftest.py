import pytest
from mdi.parser import MDIParser
from mdi.validator import MDIValidator
from mdi.profiles import GraphQLProfile


@pytest.fixture
def parser():
    return MDIParser()


@pytest.fixture
def validator():
    return MDIValidator()


@pytest.fixture
def graphql_profile():
    return GraphQLProfile()
