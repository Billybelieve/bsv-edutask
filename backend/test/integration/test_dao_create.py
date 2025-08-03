import pytest
from pymongo import MongoClient
from pymongo.errors import WriteError, DuplicateKeyError
from src.util.dao import DAO
from src.util.validators import getValidator


@pytest.fixture()
def dao_instance():
    MONGO_CONNECTION_STRING = "mongodb://root:root@edutask-mongodb:27017"
    mongo_client = MongoClient(MONGO_CONNECTION_STRING)
    database = mongo_client.edutask
    user_validator = getValidator("user")

 
    if "integration_test_users" in database.list_collection_names():
        database.drop_collection("integration_test_users")

    database.create_collection("integration_test_users", validator=user_validator)

    dao = DAO("integration_test_users")
    dao.collection.delete_many({})

    yield dao
    dao.collection.delete_many({})
    mongo_client.close()

@pytest.mark.integration_test
def test_create_user_successful(dao_instance):
    """Test successful user creation with valid data"""
    user = {
        'firstName': 'abdi',
        'lastName': 'majid',
        'email': 'test@test.com',
    }

    result = dao_instance.create(user)

    assert result["_id"] is not None
    
    assert result["firstName"] == user["firstName"]
    assert result["lastName"] == user["lastName"]
    assert result["email"] == user["email"]

@pytest.mark.integration_test
def test_create_user_missing_fields(dao_instance):
    """Test the create method with missing required fields."""
    user = {
        'firstName': 'abdi'

    }
    with pytest.raises(WriteError):
        dao_instance.create(user)

@pytest.mark.integration_test
def test_create_user_invalid_data_types(dao_instance):
    """Tests the create method with invalid data types in fields"""
    user = {
        'firstName': 123,  
        'lastName': True,  
        'email': 'test@test.com'
    }

    with pytest.raises(WriteError):
        dao_instance.create(user)

@pytest.mark.integration_test
def test_create_user_invalid_email(dao_instance):
    """Test create method with invalid email foramt"""
    user = {
        'firstName': 'mikel',
        'lastName': 'svensson',
        'email': 'test()test,se'  
    }

    with pytest.raises(WriteError):
        dao_instance.create(user)

@pytest.mark.integration_test
def test_create_user_duplicate_email(dao_instance):
    """Test the create method with duplicate email."""
    user1 = {
        'firstName': 'mikel',
        'lastName': 'svensson',
        'email': 'test@test.com'
    }
    user2 = {
        'firstName': 'abdi',
        'lastName': 'majid',
        'email': 'test@test.com'  
    }

    dao_instance.create(user1)

    with pytest.raises(DuplicateKeyError):
        dao_instance.create(user2)