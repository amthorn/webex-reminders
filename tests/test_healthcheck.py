
def test_healthcheck() -> None:
    from bot.bot import healthcheck
    assert healthcheck() == 'OK'
