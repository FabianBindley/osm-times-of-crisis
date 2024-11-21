import psycopg2
from psycopg2.extras import execute_values

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
    

    def insert_data(self, value_list, success_count, connection):
        self.connection = connection
        insert_query = """
            INSERT INTO public.changes (
                element_id, edit_type, element_type, timestamp, disaster_id, version, visible, changeset, tags, building, highway, coordinates, uid
            )
            VALUES %s
        """

        cursor = connection.cursor()

        # Execute the bulk insert with coordinates formatted in the query
        execute_values(
            cursor,
            insert_query,
            value_list,
            template="(%s, %s, %s, to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)"
        )

        # Commit the transaction
        self.connection.commit()

        print(f"Inserted {success_count} elements")

    
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


    def insert_disasters(self, disaster_list, connection):
        insert_query = """
            INSERT INTO public.disasters (id, country, area, area_geometry, date, h3_resolution)
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
                disaster["h3_resolution"]
            )
            for disaster in disaster_list
        ]

        # Log data to debug
        print(f"Data to insert: {data_to_insert}")

        try:
            cursor = connection.cursor()

            # Execute the bulk insert with proper formatting
            execute_values(
                cursor,
                insert_query,
                data_to_insert,
                template="(%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326), to_timestamp(%s), %s)"
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
        # Calculate the difference in time between the intervals
        delta = intervals[1] - intervals[0]

        for i in range(len(intervals)):
            start_date = intervals[i]
            end_date = start_date + delta

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


