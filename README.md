# MESA Airport Runway Simulation

This project simulates the movement of airplanes on an airport runway using the MESA framework. The simulation includes various agents representing airplanes, a model to manage the simulation environment, and visualization tools to display the results.

## Project Structure

- **src/**: Contains the main source code for the simulation.
  - **agents.py**: Defines the `Airplane` class with properties and methods for airplane behavior.
  - **model.py**: Contains the `AirportModel` class that manages the simulation environment.
  - **server.py**: Sets up the server to run the simulation.
  - **visualization.py**: Handles the visualization of the simulation.
  - **utils.py**: Contains utility functions for data processing and logging.

- **notebooks/**: Includes Jupyter notebooks for exploratory data analysis.
  - **exploration.ipynb**: Used for analyzing and visualizing simulation results.

- **data/**: Stores data files related to the simulation.
  - **runway_logs.csv**: Logs of airplane movements on the runway.

- **tests/**: Contains unit tests for the project.
  - **test_model.py**: Unit tests for the `AirportModel` class.

- **requirements.txt**: Lists the dependencies required for the project.

- **.gitignore**: Specifies files and directories to be ignored by version control.

## Setup Instructions

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using:
   ```
   pip install -r requirements.txt
   ```
4. Run the simulation server using:
   ```
   python src/server.py
   ```
5. Access the simulation through the provided URL in your browser.

## Overview of the Simulation

The simulation models the behavior of airplanes as they move along the runway, taking off and landing based on a set of defined rules. The `AirportModel` class orchestrates the simulation, while the `Airplane` class defines the properties and behaviors of individual airplanes. Visualization tools provide insights into the simulation's progress and outcomes.

## Contributing

Contributions to the project are welcome. Please submit a pull request or open an issue for any suggestions or improvements.