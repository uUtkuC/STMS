def read_query_times(file_path):
    """Read query times from a file and return them as a list of tuples."""
    query_times = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 3):
            query = lines[i].strip().replace("Query: ", "")
            exec_time = float(lines[i + 1].strip().replace("Execution Time: ", "").replace(" seconds", ""))
            query_times.append((query, exec_time))
    return query_times

def calculate_percentage_increase(old_time, new_time):
    """Calculate the percentage increase from old_time to new_time."""
    if old_time == 0:
        return float('inf')  # Return infinity if the old_time is zero
    return ((new_time - old_time) / old_time) * 100

def compare_query_times(file1, file2, output_file):
    """Compare query times from two files and write the improvements to an output file."""
    query_times1 = read_query_times(file1)
    query_times2 = read_query_times(file2)

    with open(output_file, 'w') as file:
        file.write("Comparison of Query Execution Times\n")
        file.write("==================================\n\n")
        for (query1, time1), (query2, time2) in zip(query_times1, query_times2):
            if query1 == query2:
                time_diff = time2 - time1
                perc_increase = calculate_percentage_increase(time1, time2)
                file.write(f"Query: {query1}\n")
                file.write(f"Time in {file1}: {time1:.6f} seconds\n")
                file.write(f"Time in {file2}: {time2:.6f} seconds\n")
                file.write(f"Time Difference: {time_diff:.6f} seconds\n")
                file.write(f"Percentage Increase: {perc_increase:.2f}%\n\n")

if __name__ == "__main__":
    file1 = 'query_times_no_indices.txt'
    file2 = 'query_times_with_indices.txt'
    output_file = 'time_improvement_with_indices.txt'
    compare_query_times(file1, file2, output_file)
