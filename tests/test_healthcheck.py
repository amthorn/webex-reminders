
def test_healthcheck() -> None:
    from bot import healthcheck
    assert healthcheck() == 'OK'
