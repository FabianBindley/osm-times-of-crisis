import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
class DB_Utils:
    def __init__(self):
        self.connection = None

    def db_connect(self):
        # Connection parameters
        self.connection  = psycopg2.connect(
            dbname="postgres",
            user="fabian",
            password="hsu1s80ajA",
            host="localhost",
            port="5432"  # Default port for PostgreSQL
        )

        return self.connection 
    

    def insert_data(self, value_list, success_count, connection, three_years_pre):
        self.connection = connection

        if three_years_pre:
            insert_query = """
            INSERT INTO public.changes_3_year_pre (
                element_id, edit_type, element_type, timestamp, disaster_id, version, visible, changeset, tags, building, highway, coordinates, uid, geojson_verified
            )
            VALUES %s
            ON CONFLICT (element_id, disaster_id, version) DO NOTHING
        """
        else:
            insert_query = """
                INSERT INTO public.changes (
                    element_id, edit_type, element_type, timestamp, disaster_id, version, visible, changeset, tags, building, highway, coordinates, uid, geojson_verified
                )
                VALUES %s
                ON CONFLICT (element_id, disaster_id, version) DO NOTHING
            """

        cursor = connection.cursor()

        # Execute the bulk insert with coordinates formatted in the query
        execute_values(
            cursor,
            insert_query,
            value_list,
            template="(%s, %s, %s, to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s)"
        )

        # Commit the transaction
        self.connection.commit()

        print(f'Inserted {success_count} elements into {"changes_3_year_pre" if three_years_pre else "changes"} for disaster: {value_list[0][4]}')

    
    def update_data(self, update_list, connection, column_to_update):
        
        cursor = connection.cursor()

        cursor.execute("""
            DROP TABLE IF EXISTS temp_updates;
        """)

        cursor.execute("""
            CREATE TEMP TABLE temp_updates (
                column_value BIGINT,
                element_id BIGINT,
                version INTEGER
            );
        """)

        temp_insert_query = """
            INSERT INTO temp_updates (column_value, element_id, version)
            VALUES %s
        """

        cursor = connection.cursor()

        # Execute the bulk insert with coordinates formatted in the query
        execute_values(cursor, temp_insert_query, update_list)


        # Commit the transaction
        connection.commit()

        cursor.execute(f"""
            UPDATE public.changes
            SET {column_to_update} = temp_updates.column_value
            FROM temp_updates
            WHERE changes.element_id = temp_updates.element_id
            AND changes.version = temp_updates.version;
        """)

        print(f"Updated {cursor.rowcount} elements")
        return cursor.rowcount
    
    def delete_disasters(self):
        delete_query = """
            DELETE FROM public.disasters;
        """
        
        # Commit the transaction
        cursor = self.connection.cursor()
        cursor.execute(delete_query)
        self.connection.commit()  

    def insert_disasters(self, disaster_list, connection):
        insert_query = """
            INSERT INTO public.disasters (id, country, area, area_geometry, date, h3_resolution, disaster_type)
            VALUES %s
            ON CONFLICT (id)
            DO NOTHING;
        """

        # Transform dictionaries into tuples
        data_to_insert = [
            (
                disaster["id"],
                disaster["country"],  # Ensure this matches the column type (likely TEXT[] or JSON)
                disaster["area"],  # Ensure this matches the column type (likely TEXT[] or JSON)
                disaster["geometry"].wkt,  # Convert Shapely geometry to WKT
                disaster["date"],  # This is already a UNIX timestamp
                disaster["h3_resolution"],
                disaster["disaster_type"]
            )
            for disaster in disaster_list
        ]

        # Log data to debug
        #print(f"Data to insert: {data_to_insert}")

        try:
            cursor = connection.cursor()

            # Execute the bulk insert with proper formatting
            execute_values(
                cursor,
                insert_query,
                data_to_insert,
                template="(%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326), to_timestamp(%s), %s, %s)"
            )

            # Commit the transaction
            connection.commit()

            print(f"Inserted {len(data_to_insert)} disasters.")

        except Exception as e:
            print(f"Error inserting disasters: {e}")
            connection.rollback()  # Roll back if there's an error



        
    def count_changes_in_interval(self, disaster_id, intervals):
        results = []

        cursor = self.connection.cursor()

        for i in range(len(intervals)-1):
            start_date = intervals[i]
            end_date = intervals[i+1]

            # Query to count changes within the interval for the given disaster_id
            query = """
                SELECT COUNT(*)
                FROM changes
                WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s;
            """
            cursor.execute(query, (disaster_id, start_date, end_date))
            total_count = cursor.fetchone()[0]

            # Query to count changes within the interval for the given disaster_id
            query = """
                SELECT COUNT(*)
                FROM changes
                WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s AND edit_type = 'create';
            """
            cursor.execute(query, (disaster_id, start_date, end_date))
            create_count = cursor.fetchone()[0]

            # Query to count changes within the interval for the given disaster_id
            query = """
                SELECT COUNT(*)
                FROM changes
                WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s AND edit_type = 'edit';
            """
            cursor.execute(query, (disaster_id, start_date, end_date))
            edit_count = cursor.fetchone()[0]

            # Query to count changes within the interval for the given disaster_id
            query = """
                SELECT COUNT(*)
                FROM changes
                WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s AND edit_type = 'delete';
            """
            cursor.execute(query, (disaster_id, start_date, end_date))
            delete_count = cursor.fetchone()[0]

            # Append results as a tuple of (start_date, end_date, count)
            results.append((create_count, edit_count, delete_count,total_count))
        return results
    

    def count_changes_in_interval_3_years_pre(self, disaster_id, intervals):
        results = []
        cursor = self.connection.cursor()
        # Calculate the difference in time between the intervals
        delta = intervals[1] - intervals[0]

        for i in range(len(intervals)-1):
            start_date = intervals[i]
            end_date = intervals[i+1]

            # Query to count changes within the interval for the given disaster_id
            query = """
                SELECT COUNT(*)
                FROM changes_3_year_pre
                WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s;
            """
            cursor.execute(query, (disaster_id, start_date, end_date))
            total_count = cursor.fetchone()[0]

            # Query to count changes within the interval for the given disaster_id
            query = """
                SELECT COUNT(*)
                FROM changes_3_year_pre
                WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s AND edit_type = 'create';
            """
            cursor.execute(query, (disaster_id, start_date, end_date))
            create_count = cursor.fetchone()[0]

            # Query to count changes within the interval for the given disaster_id
            query = """
                SELECT COUNT(*)
                FROM changes_3_year_pre
                WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s AND edit_type = 'edit';
            """
            cursor.execute(query, (disaster_id, start_date, end_date))
            edit_count = cursor.fetchone()[0]

            # Query to count changes within the interval for the given disaster_id
            query = """
                SELECT COUNT(*)
                FROM changes_3_year_pre
                WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s AND edit_type = 'delete';
            """
            cursor.execute(query, (disaster_id, start_date, end_date))
            delete_count = cursor.fetchone()[0]

            # Append results as a tuple of (start_date, end_date, count)
            results.append((create_count, edit_count, delete_count,total_count))
        return results
    


    def get_changes_in_interval(self, start_date, end_date, disaster_id):

        query = """
            SELECT element_id, element_type, edit_type, timestamp, coordinates
            FROM changes
            WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s;
        """
        

        cursor = self.connection.cursor()
        cursor.execute(query, (disaster_id, start_date, end_date))

        return cursor.fetchall()
    


    def get_disaster_with_id(self, disaster_id):
        cursor = self.connection.cursor()

        disaster_query = f"""
        SELECT * FROM disasters WHERE id = {disaster_id}
        """

        cursor.execute(disaster_query)

        return cursor.fetchone()
    

    def get_broken_coordinates(self, disaster_id):
        cursor = self.connection.cursor()

        # Coordinates are broken if they are at 0,0 and have the value - 0101000020E610000000000000000000000000000000000000

        changes_query = f"""
        SELECT id, element_id, disaster_id, coordinates, version, element_type, visible FROM changes WHERE coordinates = '0101000020E610000000000000000000000000000000000000' AND disaster_id = {disaster_id};
        """

        cursor.execute(changes_query)

        return cursor.fetchall()
    

    def get_changes_same_element_id(self, element_id, diaster_id):
        cursor = self.connection.cursor()

        # Coordinates are broken if they are at 0,0 and have the value - 0101000020E610000000000000000000000000000000000000

        changes_query = f"""
        SELECT id, coordinates, visible FROM changes WHERE element_id = {element_id} AND disaster_id = {diaster_id} ORDER BY version DESC;
        """

        cursor.execute(changes_query)

        return cursor.fetchall()

    def update_change_coordinates(self, id, new_coordinate):
        cursor = self.connection.cursor()
        # Coordinates are broken if they are at 0,0 and have the value - 0101000020E610000000000000000000000000000000000000

        changes_query = f"""
        UPDATE changes SET coordinates = ST_SetSRID(ST_MakePoint(%s, %s), 4326)  WHERE id = %s;
        """

        cursor.execute(changes_query, (new_coordinate[0], new_coordinate[1], id))
        self.connection.commit()  # Commit the changes to the database
        cursor.close()


    def get_detected_bulk_imports(self, changes_threshold, seconds_threshold):
        cursor = self.connection.cursor()

        bulk_imports_query = f"""
        SELECT 
            disaster_id,
            changeset, 
            uid, 
            COUNT(*) AS changes_count
        FROM 
            changes
        GROUP BY 
            disaster_id, changeset, uid
        HAVING 
            COUNT(*) > {changes_threshold} AND
            MAX(timestamp) - MIN(timestamp) <= INTERVAL '{seconds_threshold} second'
        ORDER BY 
            changes_count DESC;
        """

        cursor.execute(bulk_imports_query)
        return cursor.fetchall()
    
    def get_changesets_more_than_n_changes(self, n):
        cursor = self.connection.cursor()

        bulk_imports_query = """
        SELECT 
            changeset, 
            uid, 
            disaster_id, 
            COUNT(*) as changes_count
        FROM 
            changes
        GROUP BY 
            changeset, 
            uid, 
            disaster_id
        HAVING 
            COUNT(*) > %s
        ORDER BY
                changes_count DESC;
        """

        cursor.execute(bulk_imports_query, (n,))
        return cursor.fetchall()
    
    def get_changes_in_changeset(self, changeset):
        cursor = self.connection.cursor()

        changes_query = """
        SELECT 
            *
        FROM 
            changes
        WHERE
            changeset = %s
        ORDER BY
            timestamp ASC;
        """

        cursor.execute(changes_query, (changeset,))
        return cursor.fetchall()
    
    def copy_to_deleted_changes_table(self, changeset):
        cursor = self.connection.cursor()

        # Insert query to copy rows
        copy_query = f"""
        INSERT INTO import_filtered_changes
        SELECT * FROM changes
        WHERE changeset = {str(changeset)} ON CONFLICT (id)
        DO NOTHING;
        """

        cursor.execute(copy_query)
        self.connection.commit()
        cursor.close()
    
    def remove_changes_from_changeset(self, changeset):
        cursor = self.connection.cursor()
        delete_query = f"""
        DELETE FROM changes WHERE changeset = '{changeset}';
        """

        print(f"Deleting changes for changeset: {changeset}")
        cursor.execute(delete_query)
        deleted_count = cursor.rowcount  # Capture how many rows were deleted

        self.connection.commit()  

       # delete_query = f"""
        #DELETE FROM changes_3_year_pre WHERE changeset = '{changeset}';
        #"""

        #print(f"Deleting changes_3_year_pre for changeset: {changeset}")
        cursor.execute(delete_query)
        self.connection.commit()  

        cursor.close()
        return deleted_count


    def verify_changes_geojson(self, disaster_id):
        cursor = self.connection.cursor()
        # Count total changes for the disaster
        count_total_query = """
        SELECT COUNT(*)
        FROM changes
        WHERE disaster_id = %s;
        """
        cursor.execute(count_total_query, (disaster_id,))
        total = cursor.fetchone()[0]

        print(f"Total: {total}")
        print(f"Checking coordinates:")
        # Update changes that are within the disaster's geojson boundary
        update_query = """
        UPDATE changes
        SET geojson_verified = TRUE
        WHERE disaster_id = %s AND
            ST_Contains(
                (SELECT area_geometry FROM disasters WHERE id = %s),
                coordinates
            );
        """
        cursor.execute(update_query, (disaster_id, disaster_id))

        # Count valid changes
        count_valid_query = """
        SELECT COUNT(*)
        FROM changes
        WHERE disaster_id = %s AND geojson_verified = TRUE;
        """
        cursor.execute(count_valid_query, (disaster_id,))
        valid = cursor.fetchone()[0]

        # Commit the transaction
        self.connection.commit()
        cursor.close()

        return valid, total
    

    def remove_invalid(self, disaster_id):
        cursor = self.connection.cursor()

        # Insert query to copy rows
        copy_query = f"""
        INSERT INTO import_filtered_changes
        SELECT * FROM changes
        WHERE disaster_id = {disaster_id} AND geojson_verified = False ON CONFLICT (id)
        DO NOTHING;
        """
        print(f"Copying invalid changes for disaster_id: {disaster_id}")
        cursor.execute(copy_query)

        delete_query = f"""
        DELETE FROM changes WHERE disaster_id = {disaster_id} AND geojson_verified = False;
        """
        print(f"Deleting invalid changes for disaster_id: {disaster_id}")
        cursor.execute(delete_query)

        #delete_query = f"""
        #DELETE FROM changes_3_year_pre WHERE disaster_id = {disaster_id} AND geojson_verified = False;
        #"""
        #print(f"Deleting invalid changes for disaster_id: {disaster_id}")
        #cursor.execute(delete_query)
        removed_count = cursor.rowcount

        self.connection.commit()  
        cursor.close()
        
        return removed_count
    

    def get_tag_key_usage(self):
        cursor = self.connection.cursor()

        # Query to get the count of each tag
        tag_key_count_query = """
        SELECT key, COUNT(*) AS usage_count
            FROM (
                SELECT jsonb_object_keys(tags) AS key
                FROM changes
                WHERE tags IS NOT NULL
            ) subquery
            GROUP BY key
            ORDER BY usage_count DESC, key;
        """

        cursor.execute(tag_key_count_query)
        return cursor.fetchall()
    
    def get_tag_key_usage_for_disaster(self, disaster_id, intervals):
        cursor = self.connection.cursor()

        # Query to get the count of each tag
        tag_key_count_query = """
        SELECT key, COUNT(*) AS usage_count
            FROM (
                SELECT jsonb_object_keys(tags) AS key
                FROM changes
                WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s AND tags IS NOT NULL
            ) subquery
            GROUP BY key
            ORDER BY usage_count DESC, key;
        """

        results = []
        for i in range(len(intervals)-1):
            start_date = intervals[i]
            end_date = intervals[i+1]

            cursor.execute(tag_key_count_query, (disaster_id, start_date, end_date))
            results.append(cursor.fetchall())

        return results
    

    def get_total_changes(self, pre_disaster_days, imm_disaster_days, post_diaster_days):
        cursor = self.connection.cursor()

        # Query to get the count of changes within the disaster periods
        total_changes_query = """
        SELECT COUNT(*)
        FROM changes c
        JOIN disasters d ON c.disaster_id = d.id
        WHERE c.timestamp BETWEEN (d.date - INTERVAL '%s days') AND (d.date + INTERVAL '%s days');
        """

        cursor.execute(total_changes_query, (pre_disaster_days, imm_disaster_days+post_diaster_days))
        total_changes = cursor.fetchone()[0]
        cursor.close()
        return total_changes
    

    def get_tag_key_value_usage(self, keys):
        cursor = self.connection.cursor()
        keys_sql = ", ".join(["%s"] * len(keys))

        # Query to get the count of each value for the provided keys
        tag_key_value_count_query = f"""
        SELECT key, value, COUNT(*) AS usage_count
        FROM (
            SELECT jsonb_object_keys(tags) AS key, 
                tags ->> jsonb_object_keys(tags) AS value
            FROM changes
            WHERE tags IS NOT NULL
        ) subquery
        WHERE key IN ({keys_sql})
        GROUP BY key, value
        ORDER BY key, usage_count DESC, value
        """

        # Execute the query with keys as parameters
        cursor.execute(tag_key_value_count_query, keys)
        return cursor.fetchall()

    def get_tag_key_value_usage_for_disaster(self, keys, disaster_id, intervals):
        cursor = self.connection.cursor()
        keys_sql = ", ".join(["%s"] * len(keys))

        # Query to get the count of each tag
        tag_key_count_query = f"""
        SELECT key, value, COUNT(*) AS usage_count
            FROM (
                SELECT jsonb_object_keys(tags) AS key,
                    tags ->> jsonb_object_keys(tags) AS value
                FROM changes
                WHERE disaster_id = %s AND timestamp >= %s AND timestamp < %s AND tags IS NOT NULL
            ) subquery
            WHERE key IN ({keys_sql})
            GROUP BY key, value
            ORDER BY key, usage_count DESC, value
        """

        results = []
        for i in range(len(intervals)-1):
            start_date = intervals[i]
            end_date = intervals[i+1]

            cursor.execute(tag_key_count_query, (disaster_id, start_date, end_date, *keys))
            results.append(cursor.fetchall())

        return results
    

    # if return all is true, dont sample, just return all
    def get_sample_changes_for_disaster(self, disaster_id, sample_size, sample, start_date, end_date, get_type, random, three_years_pre=False):
        cursor = self.connection.cursor()

        query = f"""
        SELECT {"element_id, disaster_id, version, edit_type, element_type" if get_type == "prepare" else "*"} FROM {"changes_3_year_pre" if three_years_pre else "changes"} WHERE disaster_id = %s AND %s <= timestamp AND timestamp <= %s  AND edit_type = 'edit' {" ORDER BY random() " if random else ""}{" LIMIT %s" if sample else ""}
        """
        if sample:
            cursor.execute(query, (disaster_id, start_date, end_date, sample_size))
        else:
            cursor.execute(query, (disaster_id, start_date, end_date))

        # Fetch all rows
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_change_with_version(self, element_id, element_type, disaster_id, version):
        cursor = self.connection.cursor()
 
        query = """
        SELECT * FROM changes WHERE element_id = %s AND element_type = %s AND disaster_id = %s AND version = %s
        """
        cursor.execute(query, (element_id, element_type, disaster_id, version))


        # Fetch all rows
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def get_existing_versions(self, version_list, get_type, three_years_pre, disaster_id):
        cursor = self.connection.cursor()
        batch_size = 5000  # Adjust based on your database limits
        result = []
        start_time = datetime.now()
        total_batches = len(version_list)//batch_size + 1
        for i in range(0, len(version_list), batch_size):
            batch = version_list[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            query = f"""
            SELECT {"element_id, disaster_id, version, element_type" if get_type == "prepare" else "*"}
            FROM changes
            WHERE (element_id, disaster_id, version, element_type) IN %s
            """
            cursor.execute(query, (tuple(batch),))
            result.extend(cursor.fetchall())

            current_time = datetime.now()
            remaining_time = (current_time-start_time)/(batch_num) * (total_batches - batch_num)
            print(f"Getting changes {disaster_id} | batch: {batch_num}/{total_batches}, estimated time remaining: {remaining_time.seconds} seconds")
            

        cursor.close()
        return result

