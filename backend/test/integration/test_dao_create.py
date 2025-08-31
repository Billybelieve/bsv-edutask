import pytest
from pymongo import MongoClient
from pymongo.errors import WriteError, DuplicateKeyError
from src.util.dao import DAO
from src.util.validators import getValidator

import os

@pytest.fixture(scope="function")
def dao_instance():
    """Setup test database connection and DAO instance"""
    # Database configuration
    db_url = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = "edutask"
    collection_name = "integration_test_users"

    # Connect to MongoDB
    client = MongoClient(db_url)
    db = client[db_name]

    # Get validator schema
    validator_schema = getValidator("user")

    # Clean up existing test collection
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)

    # Create fresh test collection with validator
    db.create_collection(collection_name, validator=validator_schema)

    # Create DAO instance
    dao = DAO(collection_name)

    # Clear any existing data
    dao.collection.delete_many({})

    # Provide DAO to tests
    yield dao

    # Cleanup after each test
    dao.collection.delete_many({})
    client.close()


@pytest.mark.integration_test
def test_create_user_successful_has_id(dao_instance):
    """User creation -> result contains _id"""
    user = {'firstName': 'abdi', 'lastName': 'majid', 'email': 'test@test.com'}
    result = dao_instance.create(user)
    assert result["_id"] is not None


@pytest.mark.integration_test
def test_create_user_successful_first_name(dao_instance):
    """User creation -> firstName matches input"""
    user = {'firstName': 'abdi', 'lastName': 'majid', 'email': 'test@test.com'}
    result = dao_instance.create(user)
    assert result["firstName"] == user["firstName"]


@pytest.mark.integration_test
def test_create_user_successful_last_name(dao_instance):
    """User creation -> lastName matches input"""
    user = {'firstName': 'abdi', 'lastName': 'majid', 'email': 'test@test.com'}
    result = dao_instance.create(user)
    assert result["lastName"] == user["lastName"]


@pytest.mark.integration_test
def test_create_user_successful_email(dao_instance):
    """User creation -> email matches input"""
    user = {'firstName': 'abdi', 'lastName': 'majid', 'email': 'test@test.com'}
    result = dao_instance.create(user)
    assert result["email"] == user["email"]


@pytest.mark.integration_test
def test_create_user_missing_fields(dao_instance):
    """Test the create method with missing required fields."""
    user = {'firstName': 'abdi'}
    with pytest.raises(WriteError):
        dao_instance.create(user)


@pytest.mark.integration_test
def test_create_user_invalid_data_types(dao_instance):
    """Tests the create method with invalid data types in fields"""
    user = {'firstName': 123, 'lastName': True, 'email': 'test@test.com'}
    with pytest.raises(WriteError):
        dao_instance.create(user)


@pytest.mark.integration_test
def test_create_user_invalid_email(dao_instance):
    """Test create method with invalid email format"""
    user = {'firstName': 'mikel', 'lastName': 'svensson', 'email': 'test()test,se'}
    with pytest.raises(WriteError):
        dao_instance.create(user)


@pytest.mark.integration_test
def test_create_user_duplicate_email(dao_instance):
    """Test the create method with duplicate email."""
    user1 = {'firstName': 'mikel', 'lastName': 'svensson', 'email': 'test@test.com'}
    user2 = {'firstName': 'abdi', 'lastName': 'majid', 'email': 'test@test.com'}
    dao_instance.create(user1)
    with pytest.raises(DuplicateKeyError):
        dao_instance.create(user2)
