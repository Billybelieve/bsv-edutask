import pytest
from src.controllers.usercontroller import UserController
from unittest.mock import MagicMock

@pytest.fixture
def mock_DAO():
    return MagicMock()

@pytest.fixture
def controller(mock_DAO):
    return UserController(mock_DAO)

def test_get_user_by_email_invalid_email(controller):
    """Invalid email string raises ValueError"""
    with pytest.raises(ValueError):
        controller.get_user_by_email("invalid")

def test_get_user_by_email_no_user(mock_DAO, controller):
    """valid email user does not exist returns should retur None"""

    mock_DAO.find.return_value = []
    result = controller.get_user_by_email("test@test.com")

    assert result is None

def test_get_user_by_email_one_user(mock_DAO, controller):
    """Valid emai one user found returns User object"""
    mock_DAO.find.return_value = [{"user-name": "mikel"}]
    result = controller.get_user_by_email("test@test.com")
    assert result == {"user-name": "mikel"}

def test_get_user_by_email_db_exception(mock_DAO, controller):
    """Valid email Database failure raises Exception"""
    mock_DAO.find.side_effect = Exception("Db error")
    with pytest.raises(Exception) as exc_info:
        controller.get_user_by_email("test@test.com")
    assert str(exc_info.value) == "Db error"

def test_get_user_by_email_multiple_users(mock_DAO, controller, capfd):
    """Valid email multiple users found returns first User object & prints warning"""
    mock_DAO.find.return_value = [
        {"user-name": "mikel"},
        {"user-name": "abdi"}
    ]


    result = controller.get_user_by_email("test@test.com")
    out, _ = capfd.readouterr()
    assert result == {"user-name": "mikel"}
    assert "more than one user found with mail test@test.com" in out
