import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from pymongo.errors import ConnectionFailure
from functions import db

class TestDatabaseFunctions(unittest.TestCase):

    @patch('functions.MongoClient')
    def test_get_collection_success(self, mock_client):
        # Mock MongoClient to simulate successful connection
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        collection = db.get_collection("test_db", "test_collection", "mongodb://test_uri")
        self.assertEqual(collection, mock_collection)

    @patch('functions.MongoClient')
    def test_get_collection_failure(self, mock_client):
        # Simulate a connection failure
        mock_client.side_effect = ConnectionFailure("Connection failed")
        
        with self.assertRaises(Exception) as context:
            db.get_collection("test_db", "test_collection", "mongodb://test_uri")
        
        self.assertIn("Failed to connect to MongoDB", str(context.exception))

    @patch('functions.Collection')
    def test_store_processed_data_success(self, mock_collection):
        # Simulate a successful update
        mock_collection.update_one.return_value.matched_count = 1
        document_id = ObjectId()
        processed_data = {"key": "value"}
        
        try:
            db.store_processed_data(document_id, processed_data, mock_collection)
        except Exception as e:
            self.fail(f"store_processed_data raised an exception unexpectedly: {e}")

        mock_collection.update_one.assert_called_once_with(
            {"_id": document_id},
            {"$set": processed_data}
        )

    @patch('functions.Collection')
    def test_store_processed_data_no_document_found(self, mock_collection):
        # Simulate no document found during update
        mock_collection.update_one.return_value.matched_count = 0
        document_id = ObjectId()
        processed_data = {"key": "value"}
        
        with self.assertLogs('functions.logging', level='WARNING') as log:
            db.store_processed_data(document_id, processed_data, mock_collection)
            self.assertIn(f"Tried to process (NLP) but no document found with ID: {document_id}", log.output[0])

    @patch('functions.Collection')
    def test_store_processed_data_exception(self, mock_collection):
        # Simulate an exception during the update
        mock_collection.update_one.side_effect = Exception("Update failed")
        document_id = ObjectId()
        processed_data = {"key": "value"}
        
        with self.assertRaises(Exception) as context:
            db.store_processed_data(document_id, processed_data, mock_collection)
        
        self.assertIn("Error updating (post NLP) document ID", str(context.exception))

if __name__ == '__main__':
    unittest.main()