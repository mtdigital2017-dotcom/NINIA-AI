from api.main import OperationalRunRequest


def test_operational_run_disables_training_by_default():
    payload = OperationalRunRequest()

    assert payload.train_if_ready is False
    assert payload.max_documents_per_source == 3
    assert payload.max_total_documents == 10
