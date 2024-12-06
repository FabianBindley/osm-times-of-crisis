from db_utils import DB_Utils
import matplotlib.pyplot as plt
# Perform bulk import detection
if __name__ == "__main__":
    utils = DB_Utils()
    utils.db_connect()

    detected_bulk_imports = utils.get_detected_bulk_imports()
    changeset_sizes = [bulk_import[2] for bulk_import in detected_bulk_imports]

    # Generate a histogram of changeset sizes
    plt.figure(figsize=(10, 6))
    plt.hist(changeset_sizes, bins=100, edgecolor='black')
    plt.title('Frequency Distribution of Large Changesets', fontsize=16)
    plt.xlabel('Number of Changes', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Display the histogram
    plt.savefig("Results/BulkImportDetection/BulkImportChangesetSizeHistogram.png", dpi=300, bbox_inches='tight')


    for bulk_import in detected_bulk_imports:
        changeset = bulk_import[0]
        uid = bulk_import[1]
        count = bulk_import[2]
        print(f"changeset: {changeset} uid: {uid} count: {count}")

        utils.copy_to_deleted_changes_table(changeset)
        utils.remove_changes_from_changeset(changeset)

