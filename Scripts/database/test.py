from db_utils import DB_Utils
from BulkImportHandler import BulkImportHandler
from datetime import datetime, timezone
import time
import json
from shapely import wkb

if __name__ == "__main__":
 
    utils = DB_Utils()
    connection = utils.db_connect()

    coords = "0101000020E61000000C7112358F6A15402258BEFDCE7D3C40"
    print(list(wkb.loads(coords).coords)[0])
