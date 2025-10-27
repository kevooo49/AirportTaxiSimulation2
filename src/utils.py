def load_runway_data(file_path):
    import pandas as pd
    return pd.read_csv(file_path)

def log_airplane_movement(airplane_id, position, status):
    with open('runway_logs.csv', 'a') as log_file:
        log_file.write(f"{airplane_id},{position},{status}\n")