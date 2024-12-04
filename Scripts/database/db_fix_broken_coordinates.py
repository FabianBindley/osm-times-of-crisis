from db_utils import DB_Utils
from BulkUpdateHandler import BulkUpdateHandler
from datetime import datetime, timezone
from shapely import wkb

if __name__ == "__main__":
 
    utils = DB_Utils()
    utils.db_connect()

    changes = utils.get_broken_coordinates()

    # [(64180249, '0101000020E6100000C27751AAB31B5540CE797C314AAC3B40', True), (64180250, '0101000020E610000000000000000000000000000000000000', False)]

    for change in changes:
        id = change[0]
        element_id = change[1]
        diaster_id = change[2]
        coordinates = change[3]
 
        changes_same_element_id = utils.get_changes_same_element_id(element_id, diaster_id)

        if len(changes_same_element_id) > 0:
            for change_same_element_id in changes_same_element_id:

                update_id = change_same_element_id[0]
                update_coordinates = change_same_element_id[1]
                
                if update_coordinates != "0101000020E610000000000000000000000000000000000000" and update_id!=id:
                    coords = list(wkb.loads(update_coordinates).coords)[0]
                    utils.update_change_coordinates(id, ( coords[0], coords[1]))
                    break

        print(f"Updated id: {id} element_id: {element_id}")






    