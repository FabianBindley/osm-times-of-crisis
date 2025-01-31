from db_utils import DB_Utils
import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta
import pickle
# Perform bulk import detection
def get_changesets(n):
    changesets = db_utils.get_changesets_more_than_n_changes(n)
    with open(f"./Results/BulkImportDetection/changesets_more_than_{n}.pkl", "wb") as f:
        pickle.dump(changesets, f)

def check_possible_import_timestamp_range(changeset, changes, minutes):

    first_change = changes[0]
    last_change = changes[-1]

    time_difference = last_change[4] - first_change[4]
    #print(changeset)
    if time_difference < timedelta(minutes=minutes):
        #print(changes[0])
        #print(changes[-1])
        #print(f"less than {minutes} mins")
        #print(time_difference)
        return True
    else:
        #print("not less")
        #print(changes[0])
        #print(changes[-1])
        #print(time_difference)
        return False

def check_number_of_creates(changeset,changes, percent):

    sum_creates = 0
    sum_edits = 0
    sum_deletes = 0
    for change in changes:
        edit_type = change[3]

        if edit_type == "create":
            sum_creates += 1

        if edit_type == "edit":
            sum_edits += 1

        if edit_type == "delete":
            sum_deletes += 1
    num_changes = len(changes)

    #print("changeset ",changeset)
    #print(sum_creates/num_changes)
    #print(sum_edits/num_changes)
    #print(sum_deletes/num_changes)

    if sum_creates/num_changes > percent or sum_edits/num_changes > percent or sum_deletes/num_changes > percent:
        #print("more dominated")
        return True
    else:
        #print("less dominated")
        return False

def remove_import_changeset(possible_import, counter, num_imports, start_time):

    changeset, uid, disaster_id, count = possible_import
    print(f"removing changes in changeset: {changeset}")

    db_utils.copy_to_deleted_changes_table(changeset)
    db_utils.remove_changes_from_changeset(changeset)

    elapsed_time = datetime.now().timestamp() - start_time.timestamp()
    minutes, seconds = divmod(int(elapsed_time), 60)

    print(f"{counter}/{num_imports}  disaster_id: {disaster_id} changeset: {changeset} uid: {uid} count: {count}")
    print(f"Time Elapsed: {minutes}m {seconds}s")
    average_time_per_batch = elapsed_time / counter  

    estimated_time_remaining = average_time_per_batch * (num_imports - counter)
    # Convert estimated time remaining to minutes and seconds
    minutes, seconds = divmod(int(estimated_time_remaining), 60)
    print(f"Estimated time remaining: {minutes}m {seconds}s")

    counter+=1

def run_filtering_with_params(n, minutes, ratio, remove_imports):
    get_changesets(n)
    with open(f"./Results/BulkImportDetection/changesets_more_than_{n}.pkl", "rb") as f:
        possible_imports = pickle.load(f)

    print(possible_imports)
    print(len(possible_imports))
    #print(sum([row[3] for row in possible_imports]))
    if remove_imports:
        counter = 1
        start_time = datetime.now()
        for possible_import in possible_imports:
            
            changeset, uid, disaster_id, count = possible_import
            changes = db_utils.get_changes_in_changeset(changeset)

            if check_possible_import_timestamp_range(changeset, changes, minutes) and check_number_of_creates(changeset, changes, ratio):
                remove_import_changeset(possible_import, counter, num_imports=len(possible_imports), start_time=start_time)
            counter+= 1



if __name__ == "__main__":
    db_utils = DB_Utils()
    db_utils.db_connect()

    remove_imports = False

    n = 5000
    minutes = 30
    ratio = 0.95

    #run_filtering_with_params(n=5000, minutes=30, ratio=0.95, True)
    run_filtering_with_params(n=3000, minutes=1, ratio=0.95, remove_imports =True)
    # What is a bulk import?
    # 1) More than n changes in a changeset
    # 2) 95% or more creates
    # 3) Within 30 mins
