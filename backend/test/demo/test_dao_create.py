import pytest
from pymongo import MongoClient
from src.util.dao import DAO
from unittest.mock import patch
import pymongo
from pymongo.errors import WriteError
import os

@pytest.fixture(scope="module")
def dao():
    """Fixture that provides DAOs for different collections using a test database"""
    # Define the test MongoDB URL with authentication and authSource
    test_mongo_url = 'mongodb://root:root@localhost:27017/test_edutask_integration?authSource=admin'
    
    # Patch the environment variable MONGO_CONNECTION_STRING which is used by the DAO
    with patch.dict('os.environ', {'MONGO_CONNECTION_STRING': test_mongo_url}):
        # Create a MongoClient instance using the patched environment variable
        client = MongoClient(os.getenv('MONGO_CONNECTION_STRING'))

        # Drop the test database to ensure a clean state (requires authentication)
        print(f"Dropping database test_edutask_integration using URL: {test_mongo_url}") # Added for debugging
        client.drop_database("test_edutask_integration")

        # Initialize DAO instances for each collection type
        # The DAO constructor will use the patched MONGO_CONNECTION_STRING
        yield {
            'task': DAO("task"),
            'todo': DAO("todo"),
            'user': DAO("user"),
            'video': DAO("video")
        }
        
        # Teardown: drop the test database after tests (requires authentication)
        print(f"Dropping database test_edutask_integration during teardown using URL: {test_mongo_url}") # Added for debugging
        client.drop_database("test_edutask_integration")

@pytest.fixture(autouse=True)
def cleanup_collection(validator, dao):
    """Fixture that ensures test isolation by cleaning up collections before and after each test"""
    collection_name = validator[0]
    # Drop the collection using the DAO instance from the 'dao' fixture
    # This operation should work with the authenticated client used by the DAO
    dao[collection_name].drop()
    yield dao[collection_name]
    dao[collection_name].drop()

test_data = {
    "task": {
        "valid": {
            "data": {
                "title": "test",
                "description": "test",
            },
            "result": {
                "title": "test",
                "description": "test",
                "_id": "000000000000000000000001"
            },
            "test_type": "valid"
        },
        "missing_required": {
            "data": {
                "title": "test"
            },
            "result": "WriteError",
            "test_type": "missing_required"
        },
        "invalid_property": {
            "data": {
                "title": 123,
                "description": "test",
                "todos": 123,
            },
            "result": "WriteError",
            "test_type": "invalid_property"
        }
    },
    "todo": {
        "valid": {
            "data": {
                "description": "test",
                "done": True,
            },
            "result": {
                "description": "test",
                "done": True,
                "_id": "000000000000000000000001"
            },
            "test_type": "valid"
        },
        "invalid_property": {
            "data": {
                "description": 123,
                "done": "test",
            },
            "result": "WriteError",
            "test_type": "invalid_property"
        },
        "missing_required": {
            "data": {
                "done": True,
            },
            "result": "WriteError",
            "test_type": "missing_required"
        }
    },
    "user": {
        "valid": {
            "data": {
                "firstName": "mikel",
                "lastName": "yoloson",
                "email": "test@test.com"
            },
            "result": {
                "firstName": "mikel",
                "lastName": "yoloson",
                "email": "test@test.com",
                "_id": "000000000000000000000001"
            },
            "test_type": "valid"
        },
        "missing_required": {
            "data": {
                "firstName": "baa",
                "lastName": "wikell"
            },
            "result": "WriteError",
            "test_type": "missing_required"
        },
        "invalid_property": {
            "data": {
                "firstName": "hibo",
                "lastName": "heja",
                "email": "test@test.com",
                "tasks": "test"
            },
            "result": "WriteError",
            "test_type": "invalid_property"
        }
    },
    "video": {
        "valid": {
            "data": {
                "url": "https://www.youtube.com/watch?v=example"
            },
            "result": {
                "url": "https://www.youtube.com/watch?v=example",
                "_id": "000000000000000000000001"
            },
            "test_type": "valid"
        },
        "missing_required": {
            "data": {},
            "result": "WriteError",
            "test_type": "missing_required"
        },
        "invalid_property": {
            "data": {
                "url": 123,
                "NAN": "test"
            },
            "result": "WriteError",
            "test_type": "invalid_property"
        }
    }
}

@pytest.mark.parametrize(("validator", "test_data"),
                         [
                             (["todo"], test_data["todo"]["valid"]),
                             (["todo"], test_data["todo"]["invalid_property"]),
                             (["todo"], test_data["todo"]["missing_required"]),
                             (["user"], test_data["user"]["valid"]),
                             (["user"], test_data["user"]["invalid_property"]),
                             (["user"], test_data["user"]["missing_required"]),
                             (["video"], test_data["video"]["valid"]),
                             (["video"], test_data["video"]["invalid_property"]),
                             (["video"], test_data["video"]["missing_required"]),
                             (["task"], test_data["task"]["valid"]),
                             (["task"], test_data["task"]["invalid_property"]),
                             (["task"], test_data["task"]["missing_required"]),
                         ])
def test_dao_create_basic_functions(validator, test_data, cleanup_collection):
    """
    Integration test for DAO create method.
    Tests the communication between DAO and MongoDB, verifying:
    1. Successful creation of valid documents
    2. Proper validation of document structure
    3. Error handling for invalid documents
    """
    collection_name = validator[0]
    input_data = test_data["data"]
    expected_result = test_data["result"]
    
    test_type = test_data["test_type"]
    
    print(f"\nTesting {collection_name} collection - {test_type}")
    print(f"Input data: {input_data}")
    print(f"Expected result: {expected_result}")
    
    if expected_result == "WriteError":
        with pytest.raises(WriteError):
            cleanup_collection.create(input_data)
    else:
        result = cleanup_collection.create(input_data)
        assert "_id" in result
        result.pop("_id")
        expected = expected_result.copy()
        expected.pop("_id")
        assert result == expected