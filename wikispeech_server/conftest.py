import pytest
import requests

@pytest.fixture(scope="session")
def client():
    session = requests.Session()
    # Don't set Content-Type here, since it messes up "data" content
    # type used in POST tests
    #session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:10000"
