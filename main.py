import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from sklearn.ensemble import IsolationForest

# Global variables for plot
fig, ax = None, None

# Isolation Forest-based anomaly detection
def detect_anomalies_isolation_forest(data, contamination=0.01):
    """
    Detect anomalies in a given dataset using the Isolation Forest method.
    """
    # Extract the 'value' column and reshape for IsolationForest
    values = data[['value']].values

    # Fit IsolationForest model
    isolation_forest = IsolationForest(contamination=contamination, random_state=42)
    data['anomaly'] = isolation_forest.fit_predict(values)

    # Calculate mean and standard deviation for the value column
    data['mean'] = data['value'].rolling(window=5, min_periods=1).mean()
    data['std_dev'] = data['value'].rolling(window=5, min_periods=1).std()

    # Isolation Forest marks anomalies as -1, normal points as 1
    anomalies = data[data['anomaly'] == -1]
    return anomalies

# Visualization function for the data stream and anomalies
def visualize_data(data, anomalies):
    """
    Visualize the data stream and detected anomalies using IsolationForest.
    The data stream is shown as a line, with anomalies marked as red dots.
    """
    global ax
    ax.clear()  # Clear previous plot
    
    # Plot the full dataset as a line
    ax.plot(data['timestamp'], data['value'], label='Data Stream', color='blue')
    
    # Plot anomalies as red dots
    if not anomalies.empty:
        ax.scatter(anomalies['timestamp'], anomalies['value'], color='red', label='Anomalies', zorder=5)

    # Set dynamic Y-axis label based on the dataset
    if current_data['name'] == 'CPU Utilization':
        ax.set_ylabel('CPU Utilization (%)')
    elif current_data['name'] == 'Temperature Data':
        ax.set_ylabel('Temperature (°C)')
    else:
        ax.set_ylabel('Taxi Demand (rides)')
    
    ax.set_title(f'Data Stream with IsolationForest Anomalies')
    ax.set_xlabel('Timestamp')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    
    # Adjust the axes limits to fit the new data
    ax.relim()
    ax.autoscale_view()

    # Redraw the updated figure
    fig.canvas.draw_idle()

# Function to save anomalies to a CSV file
def save_anomalies_to_csv(anomalies):
    """
    Save the detected anomalies to a CSV file with time, value, mean, and std deviation.
    The filename should reflect the current dataset (CPU, Temperature, NYC Taxi).
    """
    # Determine the filename based on the current dataset
    if current_data['name'] == 'CPU Utilization':
        filename = 'cpu_anomalies.csv'
    elif current_data['name'] == 'Temperature Data':
        filename = 'temperature_anomalies.csv'
    else:
        filename = 'nyc_taxi_anomalies.csv'

    # Save relevant columns (timestamp, value, mean, standard deviation) to CSV
    anomalies[['timestamp', 'value', 'mean', 'std_dev']].to_csv(filename, index=False)
    print(f"Anomalies saved to {filename}")

# Function to process the entire dataset using Isolation Forest
def process_full_data(data, contamination=0.01):
    
    """
    Process the entire dataset using Isolation Forest for anomaly detection.
    
    Parameters
    ----------
    data : pandas.DataFrame
        Input data with a 'timestamp' and 'value' column.
    contamination : float, optional
        Proportion of outliers in the data, by default 0.01.
    
    Returns
    -------
    pandas.DataFrame
        Anomalies detected by Isolation Forest, with additional columns for mean and standard deviation.
    """
    anomalies = detect_anomalies_isolation_forest(data, contamination)
    visualize_data(data, anomalies)
    return anomalies

# Button click handler for switching datasets
def switch_dataset(event):
    """
    Switch to the next dataset in the list when the button is clicked.
    After switching, process the entire dataset using Isolation Forest.
    """
    global current_data, datasets
    dataset_names = list(datasets.keys())
    current_index = dataset_names.index(current_data['name'])
    
    # Switch to the next dataset in the list
    new_index = (current_index + 1) % len(datasets)
    current_data['data'] = datasets[dataset_names[new_index]]
    current_data['name'] = dataset_names[new_index]
    
    print(f"Switched to {current_data['name']} Dataset")
    
    # Process the entire dataset after switching
    process_full_data(current_data['data'])

# Button click handler for saving anomalies
def save_anomalies(event):
    """
    Save the detected anomalies to a CSV file when the button is clicked.
    The CSV file will be named after the current dataset.
    """
    anomalies = process_full_data(current_data['data'])
    save_anomalies_to_csv(anomalies)

# Main function
def main():
    """
    Main function to load datasets and set up the visualization window.
    
    Global variables:
        cpu_data, temperature_data, nyc_taxi: DataFrames loaded from CSV files
        current_data: Dictionary containing the current dataset, with keys 'name' and 'data'
        datasets: Dictionary containing all the datasets, with keys as dataset names and values as DataFrames
        fig, ax: Matplotlib figure and axes objects
    
    Actions:
        Load datasets from CSV files
        Convert timestamps to pandas datetime for better handling
        Store datasets in a dictionary for easier access
        Initialize the current dataset (starting with CPU Utilization)
        Set up the plot window with buttons for switching datasets and exporting anomalies
        Create switch dataset button and export to CSV button
        Initial visualization with the full dataset using Isolation Forest
    """
    global cpu_data, temperature_data, nyc_taxi, current_data, datasets, fig, ax

    # Load datasets
    cpu_data = pd.read_csv('ec2_cpu_utilization_24ae8d.csv')
    temperature_data = pd.read_csv('ambient_temperature_system_failure.csv')
    nyc_taxi = pd.read_csv('nyc_taxi.csv')

    # Convert timestamps to pandas datetime for better handling
    cpu_data['timestamp'] = pd.to_datetime(cpu_data['timestamp'])
    temperature_data['timestamp'] = pd.to_datetime(temperature_data['timestamp'])
    nyc_taxi['timestamp'] = pd.to_datetime(nyc_taxi['timestamp'])

    # Store datasets in a dictionary for easier access
    datasets = {
        'CPU Utilization': cpu_data,
        'Temperature Data': temperature_data,
        'NYC Taxi': nyc_taxi
    }

    # Initialize the current dataset (starting with CPU Utilization)
    current_data = {'name': 'CPU Utilization', 'data': datasets['CPU Utilization']}

    # Set up the plot window with buttons for switching datasets and exporting anomalies
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.subplots_adjust(bottom=0.2)  # Adjust space for the buttons

    # Create switch dataset button
    ax_button_switch = plt.axes([0.7, 0.05, 0.1, 0.075])
    button_switch = Button(ax_button_switch, 'Switch Data')
    button_switch.on_clicked(switch_dataset)

    # Create export to CSV button
    ax_button_save = plt.axes([0.8, 0.05, 0.1, 0.075])
    button_save = Button(ax_button_save, 'Export CSV')
    button_save.on_clicked(save_anomalies)

    # Initial visualization with the full dataset using Isolation Forest
    process_full_data(current_data['data'])

    plt.show()

if __name__ == "__main__":
    main()
