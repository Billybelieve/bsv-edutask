import pytest
from src.controllers.usercontroller import UserController

from unittest.mock import MagicMock

# mocking the DAO user by the controller class
@pytest.fixture
def mock_DAO():
    return MagicMock()

@pytest.fixture
def controller(mock_DAO):
    return UserController(mock_DAO)

# parameterized valid cases

@pytest.mark.parametrize(
    ("mock_return", "correct_result"),
    [
        ([{"user-name": "mikel"}], {"user-name": "mikel"}),  # one user
        (None, None),  # no users
        ([{"user-name": "mikel"}, {"user-name": "abdi"}], {"user-name": "mikel"}),  # multiple users
    ]
)
def test_get_user_by_email(mock_DAO, controller, mock_return, correct_result):
    mock_DAO.find.return_value = mock_return
    result = controller.get_user_by_email("test@test.com")
    assert result == correct_result
    
    
def  test_get_user_by_email_invalid_email(controller):
    with pytest.raises(ValueError):
        controller.get_user_by_email("invalid")
        
def test_get_user_by_email_exception_raise(mock_DAO, controller):
    mock_DAO.find.side_effect = Exception("Db error")
    with pytest.raises(Exception):
        controller.get_user_by_email("test@tet.com")