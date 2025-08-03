import pytest
from src.controllers.usercontroller import UserController
from unittest.mock import MagicMock

@pytest.fixture
def mock_DAO():
    return MagicMock()

@pytest.fixture
def controller(mock_DAO):
    return UserController(mock_DAO)

# 1. Invalid email string -> raises ValueError
def test_get_user_by_email_invalid_email(controller):
    with pytest.raises(ValueError):
        controller.get_user_by_email("invalid")

# 2. Valid email, user does not exist -> returns None
def test_get_user_by_email_no_user(mock_DAO, controller):
    mock_DAO.find.return_value = []
    result = controller.get_user_by_email("test@test.com")
    assert result is None

# 3. Valid email, exactly one user found -> returns User object
def test_get_user_by_email_one_user(mock_DAO, controller):
    mock_DAO.find.return_value = [{"user-name": "mikel"}]
    result = controller.get_user_by_email("test@test.com")
    assert result == {"user-name": "mikel"}

# 4. Valid email, DB failure (Exception) -> raises Exception
def test_get_user_by_email_db_exception(mock_DAO, controller):
    mock_DAO.find.side_effect = Exception("Db error")
    with pytest.raises(Exception) as exc_info:
        controller.get_user_by_email("test@test.com")
    assert str(exc_info.value) == "Db error"

# 5. Valid email, multiple users found -> returns first User object & logs warning
def test_get_user_by_email_multiple_users(mock_DAO, controller, capfd):
    mock_DAO.find.return_value = [
        {"user-name": "mikel"},
        {"user-name": "abdi"}
    ]
    result = controller.get_user_by_email("test@test.com")
    out, _ = capfd.readouterr()
    assert result == {"user-name": "mikel"}
    assert "more than one user found with mail test@test.com" in out
