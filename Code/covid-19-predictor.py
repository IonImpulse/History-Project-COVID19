import numpy as np
import math
import tkinter as tk
from tkinter import filedialog
import os
import sys
import datetime
from dateutil import parser
import csv
import matplotlib.pyplot as plt

root = tk.Tk()
root.withdraw()
clear = lambda: os.system('cls')

def print_folders(input_list, previous_folder = "") :
    del input_list[0]
    
    for top_index, folder in enumerate(input_list) :
        folder_name = folder[0].split("\\")[-1]

        print("\n" + str(top_index + 1) + ") " + folder_name + ":")
        
        for index, fil in enumerate(folder[2]) :
            print(str(index + 1) + ": " + fil)
        
class patient :
    def __init__(self, sex, age, date_confirmed, date_deceased) :
        self.sex = sex
        self.age = age
        self.date_confirmed = date_confirmed
        self.date_deceased = date_deceased

class Virus_Predictor :
    def __init__(self) :  
        self.user = os.environ.get('USERNAME')
        self.root_dir = os.path.dirname(os.path.realpath(__file__))
        
        if "data.config" not in os.listdir(self.root_dir) :
            self.inital_setup()

        with open(self.root_dir.replace("/", "\\") + "\\data.config", "r") as target :
            self.config_data = target.readlines()

        self.patient_paths = []
        self.total_paths = []
        focus = 0
        
        for path in self.config_data :
            if path == "Patient Cases Paths:\n" :
                focus = 0
            elif path == "Total Cases Paths:\n" :
                focus = 1
            elif focus == 0 :
                self.patient_paths.append(eval(path))
            elif focus == 1 : 
                self.total_paths.append(eval(path))

    def inital_setup(self) :
        print("Running first-time setup...\nSelect data directory:")
        data_dir = filedialog.askdirectory()
        
        #Use os.walk to get all files and sub directories
        list_of_files = []
        for path_tuple in os.walk(data_dir):
            list_of_files.append(path_tuple)

        print_folders(list_of_files)

        print("Input folder numbers for patient cases:")
        print("Ex: 1, 2, 5, 7")

        patient_cases_files = input(":").replace(" ", "").split(",")

        print("Input folder numbers for total cases:")

        total_cases_files = input(":").replace(" ", "").split(",")

        print("Saving data config in root directory...")

        with open(self.root_dir.replace("/", "\\") + "\\data.config", "w", newline="\n") as target :
            target.write("Patient Cases Paths:")
            for path in patient_cases_files :
                target.write("\n")
                target.write(str(list_of_files[int(path) - 1]))
                
            target.write("\nTotal Cases Paths:")
            for path in total_cases_files :
                target.write("\n")
                target.write(str(list_of_files[int(path) - 1]))
                
        
    def get_data_patients(self) :
        self.patient_list = []
        patient_counting_num = 0
        now = datetime.datetime.now()
        self.maximum_age = 0
        self.patients_with_age = 0

        for folder in self.patient_paths :
            for data_file in folder[2] :
                with open(folder[0] + "\\" + data_file, "r", encoding="utf8") as target :
                    inputDataRaw = [row for row in csv.reader(target)]

                #Find each column
                sex_column = -1
                birth_year_column = -1
                age_column = -1
                confirmed_column = -1
                deceased_column = -1
                outcome_column = -1

                for index, column in enumerate(inputDataRaw[0]) :
                    if "sex" in column or "gender" in column :
                        sex_column = index
                    elif "birth" in column :
                        birth_year_column = index
                    elif "age" in column :
                        age_column = index
                    elif "confirm" in column :
                        confirmed_column = index
                    elif "decease" in column :
                        deceased_column = index
                    elif "outcome" in column :
                        outcome_column = index
                
                #Resolve birth/age
                birth_or_age = ""
                if age_column != -1 and birth_year_column != -1 :
                    birth_or_age = "birth"
                elif age_column != -1 :
                    birth_or_age = "age"
                elif birth_year_column != -1 :
                    birth_or_age = "birth"
                else :
                    print("Could not find age or birth column in following file:")
                    print(data_file[2])
                    input("Press enter to exit")
                    sys.exit()

                #Resolve death date
                death_or_outcome = ""
                if deceased_column != -1 and outcome_column != -1 :
                    death_or_outcome = "outcome"
                elif deceased_column != -1 :
                    death_or_outcome = "death"
                elif outcome_column != -1 :
                    death_or_outcome = "outcome"
                else :
                    print("Could not find death or outcome column in following file:")
                    print(data_file[2])
                    input("Press enter to exit")
                    sys.exit()
                
                #Delete header row
                del inputDataRaw[0]

                print("Config:")
                print(data_file)
                print(birth_or_age)
                print(death_or_outcome)
                print("--------------")
                for index, row in enumerate(inputDataRaw) :
                    #Add sex
                    temp_list = [row[sex_column]]
                    
                    #Add age
                    if birth_or_age == "age" :
                        if row[age_column] != "NA" and row[age_column] != "" :
                            try:
                                if len(row[age_column].replace(" ", "").split("-")) == 1 :
                                    age = float(row[age_column].replace(" ", "").split("-")[0])
                            except Exception as e:
                                age = np.mean([float(i) for i in row[age_column].replace(" ", "").split("-")])
                        else :
                            age = "NA"

                        temp_list.append(age)

                    else :
                        if row[birth_year_column] != "NA" and row[birth_year_column] != "" :
                            try:
                                age = now.year - float(row[birth_year_column])
                            except Exception as e:
                                age = now.year - numpy.mean([float(i) for i in row[birth_year_column].replace(" ", "").split("-")])
                            if age > self.maximum_age :
                                self.maximum_age = int(math.floor(age))
                            self.patients_with_age += 1
                        else :
                            age = "NA"

                        temp_list.append(age)


                    #Add confirmed date (it's not the fastest way, but hey, it works)
                    if row[confirmed_column] != "NA" and row[confirmed_column] != "" :
                        temp_list.append(parser.parse(row[confirmed_column].replace(" ", "").split("-")[0]))
                    else :
                        temp_list.append("NA")
                    
                    #Add deceased state/date
                    if death_or_outcome == "death" :
                        if row[deceased_column] != "NA" and row[deceased_column] != "" :
                            death_date = parser.parse(row[deceased_column])

                        else :
                            death_date = "alive"
                    else :
                        if row[outcome_column] == "died" or row[outcome_column] == "deceased" or row[outcome_column] == "dead" :
                            death_date = "deceased"

                        else :
                            death_date = "alive"
                    temp_list.append(death_date)
                    
                    self.patient_list.append(temp_list)
        
                    patient_counting_num += 1
    
    def build_calculator_data(self) :
        #Male, female
        avg_age_percentile = [0, 0]
        avg_mortality = [0, 0]
        
        male_age_key = []
        female_age_key = []
        #Setup age key
        #Age, chance to get it multiplier, mortality multiplier
        for i in range(self.maximum_age + 1) :
            male_age_key.append([0, 0])
            female_age_key.append([0, 0])


        #Get total numbers
        for row in self.patient_list :
            if row[1] != "NA" :
                age = int(math.floor(row[1]))

                if row[0] == "male" :
                    male_age_key[age][0] += 1
                    avg_age_percentile[0] += 1
                    if row[3] != "alive" :
                        male_age_key[age][1] += 1
                        avg_mortality[0] += 1

                else :
                    female_age_key[age][0] += 1
                    avg_age_percentile[1] += 1
                    if row[3] != "alive" :
                        female_age_key[age][1] += 1
                        avg_mortality[1] += 1
        
        print(avg_age_percentile)
        print(avg_mortality)
        avg_age_percentile = [i/len(male_age_key) for i in avg_age_percentile]
        avg_mortality = [i/len(male_age_key) for i in avg_mortality]
        print(avg_age_percentile)
        print(avg_mortality)
        for i in range(self.maximum_age + 1) :
            if male_age_key[i][0] != 0 :
                male_age_key[i][0] = male_age_key[i][0]/avg_age_percentile[0]
 
            if male_age_key[i][1] != 0 :
                male_age_key[i][1] = male_age_key[i][1]/avg_mortality[0]

            if female_age_key[i][0] != 0 :
                female_age_key[i][0] = female_age_key[i][0]/avg_age_percentile[1]

            if female_age_key[i][1] != 0 :
                female_age_key[i][1] = female_age_key[i][1]/avg_mortality[1]

        #Normalize to zero
        for i in range(self.maximum_age + 1) :
            male_age_key[i] = [male_age_key[i][0] - 1, male_age_key[i][1] - 1]
            female_age_key[i] = [female_age_key[i][0] - 1, female_age_key[i][1] - 1]
        
        print("\nSaving calculator key as csv in root dir...")
        
        with open(self.root_dir.replace("/", "\\") + "\\female_calculator_data.csv", "w", newline='') as target :
            csv_writer = csv.writer(target, dialect='excel')

            csv_writer.writerows(female_age_key)
        print("Saved female age key...")
        
        with open(self.root_dir.replace("/", "\\") + "\\male_calculator_data.csv", "w", newline='') as target :
            csv_writer = csv.writer(target, dialect='excel')

            csv_writer.writerows(male_age_key)
        print("Saved male age key...")

        return male_age_key, female_age_key

    def build_regression_model(self, male_age_key = None, female_age_key = None) :
        if male_age_key == None or female_age_key == None :
            print("Age keys not provided, reading from files...")

            with open(self.root_dir.replace("/", "\\") + "\\male_calculator_data.csv", "r", newline='') as target :
                male_age_key = [row for row in csv.reader(target)]
            with open(self.root_dir.replace("/", "\\") + "\\female_calculator_data.csv", "r", newline='') as target :
                female_age_key = [row for row in csv.reader(target)]
            
            print("Done!")
        male_range = [[i for i in range(len(male_age_key))], [float(value[0]) for value in male_age_key]]
        female_range = [[i for i in range(len(female_age_key))], [float(value[0]) for value in female_age_key]]

        male_hosp_fit = np.poly1d(np.polyfit(male_range[0], male_range[1], 5))
        female_hosp_fit = np.poly1d(np.polyfit(female_range[0], female_range[1], 5))

        xp = np.linspace(0, 120, 500)
        
        hosp = plt.figure(1)
        _ = plt.plot(male_range[0], male_range[1], '.', xp, female_hosp_fit(xp), '-', xp, male_hosp_fit(xp), '--')
        plt.ylim([-1.5, 1.5])

        male_range = [[i for i in range(len(male_age_key))], [float(value[1]) for value in male_age_key]]
        female_range = [[i for i in range(len(female_age_key))], [float(value[1]) for value in female_age_key]]
        
        male_death_fit = np.poly1d(np.polyfit(male_range[0], male_range[1], 4))
        female_death_fit = np.poly1d(np.polyfit(female_range[0], female_range[1], 4))
        
        death = plt.figure(2)
        _ = plt.plot(male_range[0], male_range[1], '.', xp, female_death_fit(xp), '-', xp, male_death_fit(xp), '--')
        plt.ylim([-1.5, 1.5])
        plt.show()
        input()
        print("\nSaving regressed calculator key as csv in root dir...")
        
        plt.clf()
        regressed_male_age_key = [[male_hosp_fit(i), male_death_fit(i)] for i in range(len(male_age_key))]
        regressed_female_age_key = [[female_hosp_fit(i), female_death_fit(i)] for i in range(len(female_age_key))]

        with open(self.root_dir.replace("/", "\\") + "\\regressed_female_calculator_data.csv", "w", newline='') as target :
            csv_writer = csv.writer(target, dialect='excel')

            csv_writer.writerows(regressed_female_age_key)
        print("Saved female age key...")

        with open(self.root_dir.replace("/", "\\") + "\\regressed_male_calculator_data.csv", "w", newline='') as target :
            csv_writer = csv.writer(target, dialect='excel')

            csv_writer.writerows(regressed_male_age_key)
        print("Saved male age key...")
        return regressed_male_age_key, regressed_female_age_key
class Outside_Variables :
    def __init__(self, UBI_amount, percent_cities_lockdown) :
        self.UBI_amount = UBI_amount
        self.percent_cities_lockdown = percent_cities_lockdown


if __name__ == "__main__":
    predictor = Virus_Predictor()
    #predictor.get_data_patients()
    #male_age_key, female_age_key = predictor.build_calculator_data()
    clean_male_age_key, clean_female_age_key = predictor.build_regression_model()