from db_utils import DB_Utils
from BulkImportHandler import BulkImportHandler
from datetime import datetime, timezone
import time
import json

if __name__ == "__main__":
 
    utils = DB_Utils()
    connection = utils.db_connect()
    # Open a cursor to perform database operations
    cursor = connection.cursor()

    data = [(1234567891011121314, "delete", "node", 1732185321, 7, 2, False, 17321, json.dumps({}), False, False, 0, 0, 12345)]
    success_count = 1
    utils.insert_data(data, success_count, connection)
