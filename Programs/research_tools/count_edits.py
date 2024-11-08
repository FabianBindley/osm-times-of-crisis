from IntervalEditCounterHandler import IntervalEditCounterHandler
from datetime import datetime, timezone

# Count the number of creates, edits and deletes per period for an extracted area
# Inputs: Start Timestamp, End Timestamp, interval
place = "Broxbourne"
file = f"./Data/{place}/{place}.osh.pbf"
# Define the date string
start_date_str = "2023-02-01"
end_date_str = "2023-07-30"


# Convert the date string to a datetime object
start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

interval="day"
interval_handler = IntervalEditCounterHandler(start_date, end_date, interval)
interval_handler.apply_file(file)
interval_handler.print_intervals()
interval_handler.output_csv(f"Results/EditCounting/{place}/count-{place}-{interval}-{start_date_str}-{end_date_str}.csv")

interval="week"
interval_handler = IntervalEditCounterHandler(start_date, end_date, interval)
interval_handler.apply_file(file)
interval_handler.print_intervals()
interval_handler.output_csv(f"Results/EditCounting/{place}/count-{place}-{interval}-{start_date_str}-{end_date_str}.csv")

interval="month"
interval_handler = IntervalEditCounterHandler(start_date, end_date, interval)
interval_handler.apply_file(file)
interval_handler.print_intervals()
interval_handler.output_csv(f"Results/EditCounting/{place}/count-{place}-{interval}-{start_date_str}-{end_date_str}.csv")
