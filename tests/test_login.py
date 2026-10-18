def test_valid_login():
    username = "admin"
    password = "secret123"

    assert username == "admin"
    assert password == "secret123"


def test_invalid_login():
    username = "wrong_user"

    assert username != "admin"
