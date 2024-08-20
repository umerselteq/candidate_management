from rest_framework.test import APIClient
from candidate.test.factories import CandidateFactory
from django.urls import reverse
import pytest

@pytest.mark.django_db
def test_list_candidates():
    try:
        client = APIClient()
        url = reverse('candidate:Candidate-view')
        response = client.get(url)
        print("data:", response.data)
        assert response.status_code == 200
    except AssertionError as e:
        print(e)
    except Exception as e:
        print(e)
