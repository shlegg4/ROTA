import numpy as np
import csv
from scipy.optimize import linear_sum_assignment
from tabulate import tabulate


class Job:
    def __init__(self, job_name: str, hourly_modifier: [], count_modifier: []):
        """

        :param job_name:
        :param hourly_modifier: 12 element array of modifiers for each hour of the day
        :param count_modifier: 12 element array of modifiers for each count of the job
        """
        self.job_name = job_name
        self.hourly_modifier = hourly_modifier
        self.count_modifier = count_modifier

    def score_function(self, staff_modifier, count, hour):
        # Exponential decay based on count and add a random number between 0 and 1
        return self.hourly_modifier[hour] * self.count_modifier[count] * staff_modifier + (np.random.rand() - 0.5) / 2

    def __repr__(self):
        return self.job_name


class StaffMember:
    def __init__(self, staff_name: str, job_preference: []):
        self.job_preferences = job_preference  # Preference for each job
        self.job_count = {key: 0 for key, _ in
                          self.job_preferences.items()}  # Count of staff.csv assigned to staff member
        self.staff_name = staff_name  # Name of staff member
        self.assigned = [" " for _ in range(12)]  # Jobs assigned to staff member. i.e. rota

    def score_jobs(self, hour):
        # create list with staff.csv sorted by score
        return [job.score_function(self.job_preferences[job], self.job_count[job], hour) for job in
                self.job_preferences]

    def assign_job(self, job, hour):
        if str(job) == "BREAK":
            # Set all counts to 0 bar break
            for key in self.job_count:
                if key != "BREAK":
                    self.job_count[key] = 0

        self.job_count[job] += 1  # Increment the count of the job

        self.assigned[hour] = job  # Assign job to staff member


class Rota:
    def __init__(self):
        self.jobs = load_jobs('jobs.csv')
        self.staff = load_staff('staff.csv', self.jobs)
        self.staff_hours = load_staff_hours('hours.csv')

    def create_rota(self):
        # Loop through hours of day
        for hour in range(12):

            # Use hungarian algorithm to assign staff.csv
            indices = np.where(self.staff_hours[hour] == 1)
            if len(indices[0]) == 0:
                continue
            cost_matrix = np.array([staff_member.score_jobs(hour) for staff_member in self.staff[indices]])

            max_cost = np.max(cost_matrix)
            modified_cost_matrix = max_cost - cost_matrix
            row_ind, col_ind = linear_sum_assignment(modified_cost_matrix)  # Hungarian algorithm, scipy function
            assignment = [(row, col) for row, col in zip(row_ind, col_ind)]

            # Assign staff.csv to staff members

            for row, col in assignment:
                self.staff[indices][row].assign_job(list(self.staff[indices][row].job_preferences.keys())[col], hour)

    def display_rota(self):
        table_data = []
        for row in self.staff:
            table_row = [row.staff_name] + row.assigned
            table_data.append(table_row)

        return table_data

    def export_rota(self):
        with open('rota.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            for row in self.staff:
                writer.writerow([row.staff_name] + row.assigned)


def load_jobs(directory):
    # Create an empty dictionary to store jobs
    _jobs = {}

    # Read the CSV file
    with open(directory, 'r') as csvfile:
        lines = csvfile.readlines()
        for line in lines[1:]:  # Skip the first line
            parts = line.strip().split(',')
            job_name = parts[0]
            code = parts[1]
            hours = list(map(float, parts[2:14]))
            count = list(map(float, parts[14:]))
            _jobs[job_name] = Job(code, hours, count)
    return _jobs


def load_staff(directory, _jobs):
    # Load in staff members from csv file.
    # Each staff member has a name and a preference for each job.

    staff_members = []
    with open(directory, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["Staff Name"]
            job_preferences = {}
            for job_name, job_code in _jobs.items():
                try:
                    val = float(row[job_name])
                except KeyError:
                    val = 1
                job_preferences[job_code] = val
            staff_member = StaffMember(name, job_preferences)
            staff_members.append(staff_member)

    return np.array(staff_members)


def load_staff_hours(directory):
    _staff_hours = []
    with open(directory, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            _staff_hours.append([int(x) for x in list(row.values())[1:]]) # Skip the first column

    # Transpose the array so that each row is an hour
    _staff_hours = np.array(_staff_hours).T
    return _staff_hours
