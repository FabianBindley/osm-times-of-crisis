from db_utils import DB_Utils
import matplotlib.pyplot as plt
from datetime import datetime, timezone
# Perform bulk import detection
if __name__ == "__main__":
    utils = DB_Utils()
    utils.db_connect()

    remove_imports = False

    print("Identifying bulk imports:")
    # Known bulk import users
    detected_bulk_imports = utils.get_detected_bulk_imports(changes_threshold=10000, seconds_threshold=1)

    num_imports = len(detected_bulk_imports)
    print(f"Detected {num_imports} bulk imports")
    print(detected_bulk_imports)

    changeset_sizes = [bulk_import[2] for bulk_import in detected_bulk_imports]

    # Generate a histogram of changeset sizes
    """
    plt.figure(figsize=(10, 6))
    plt.hist(changeset_sizes, bins=100, edgecolor='black')
    plt.title('Frequency Distribution of Large Changesets', fontsize=16)
    plt.xlabel('Number of Changes', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Display the histogram
    plt.savefig("Results/BulkImportDetection/BulkImportChangesetSizeHistogram.png", dpi=300, bbox_inches='tight')
    """

    if remove_imports:

        start_time = datetime.now()
        counter = 1
        for bulk_import in detected_bulk_imports:
            disaster_id, changeset, uid, count = bulk_import

            utils.copy_to_deleted_changes_table(changeset)
            utils.remove_changes_from_changeset(changeset)

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

    