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

def reject_outliers(data):
    percent95 = np.percentile(data, 95)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    
    iqr = q3 - q1

    upper_bound = q3 + (1.5 * iqr)

    for i in range(len(data)) :
        if data[i] > upper_bound :
            data[i] = percent95
    
    return data

    

def reject_outliers_double(data):
    data1 = reject_outliers([i[0] for i in data])
    data2 = reject_outliers([i[1] for i in data])

    output = list(zip(data1, data2))
    return output

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
            self.initial_setup()

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

    def initial_setup(self) :
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
                
    def make_world_demographics(self) :
        print("Select world demographics file")
        inputFile = filedialog.askopenfilename(filetypes = (("Comma Seperated Values","*.csv"),("All files", "*.*")))
        age_list = [0 for i in range(150)]

        with open(inputFile, "r", encoding="utf8") as target :
            input_data = [row for row in csv.reader(target)]
        
        del input_data[0]

        for row in input_data :
            age_list[int(row[5])] += float(row[9])

        output_data = []
        total = sum(age_list)
        for age in age_list :
            if age != 0 :
                output_data.append(age/total)
        
        print("Total:")
        print(total)
        print(output_data)

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
                print("Total injested patients in " + str(data_file) + " is " + str(len(inputDataRaw)))
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
                                age = now.year - np.mean([float(i) for i in row[birth_year_column].replace(" ", "").split("-")])
                            if age > self.maximum_age :
                                self.maximum_age = int(math.floor(age))
                            self.patients_with_age += 1
                        else :
                            age = "NA"

                        temp_list.append(age)


                    #Add confirmed date (it's not the fastest way, but hey, it works)
                    if row[confirmed_column] != "NA" and row[confirmed_column] != "" :
                        try :
                            temp_list.append(parser.parse(row[confirmed_column].replace(" ", "").split("-")[0]))
                        except Exception as e :
                            temp_list.append("NA")
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
        demographic_data = [0.015480710565472237, 0.01600938138167091, 0.016488033460649854, 0.016668191058116386, 0.016582092920010373, 0.016718267637079127, 0.016617103601374927, 0.016142310583201397, 0.01646126547179076, 0.015676210577199465, 0.017432822572523096, 0.015351416573085681, 0.016780613830692844, 0.01567486705650703, 0.01601731987623109, 0.016606282155822112, 0.01615526967462983, 0.01585409767120876, 0.017536981398989602, 0.01569129518276287, 0.019111516778628882, 0.01628200536032497, 0.01702119090014364, 0.01625317322168848, 0.015951645472958798, 0.017691107824178057, 0.015481061861556534, 0.015011901391881228, 0.016594743010270536, 0.0142682830224133, 0.018080169955384653, 0.013687568302710026, 0.014691867302803082, 0.013188290689249236, 0.013661893010674107, 0.01717581602872825, 0.014269294871800816, 0.013691367580071154, 0.014896751136858193, 0.013547396536933973, 0.017795345205435097, 0.013086880940845902, 0.013976065584190418, 0.012013583780866699, 0.01241283189378097, 0.015617995024589371, 0.01249145891512483, 0.01253400023962469, 0.012035404085426337, 0.009689008286461048, 0.0132381509349783, 0.009553000379724183, 0.010330284358809139, 0.010040292862622268, 0.009814862645451986, 0.0117623119567084, 0.009794479166093545, 0.008977737621800225, 0.009231169659056694, 0.0082761044686114, 0.010914186353425111, 0.007902120310007825, 0.007520234930789011, 0.006917963901512924, 0.006596523538582924, 0.00812941991902471, 0.006036021065303686, 0.005534213587328426, 0.005541593302797043, 0.0052417702019299395, 0.0069225948359554635, 0.0047155348630203014, 0.00437931439209353, 0.004059374278795312, 0.0039236239885132446, 0.004409499204115823, 0.0035042401038712034, 0.0032011358543007655, 0.0029871641919806654, 0.0027399271913362915, 0.0032894201474501002, 0.002286644814555681, 0.002091345533293794, 0.0018019261860650515, 0.0015992299864705322, 0.0016450521110464033, 0.0012591326809988875, 0.0010739897055252452, 0.0009150584633972578, 0.0007770358246808851, 0.0007768490718100189, 0.000522984250301821, 0.0004158093101009065, 0.0003211215109347836, 0.00025414559189193905, 0.00022069275343813974, 0.00015056896256160192, 0.00010915183637998213, 8.330278236337397e-05, 5.082140818853615e-05, 2.1168499350088563e-06, 1.4968061903176837e-06, 1.1685184336882117e-06, 8.203042578399553e-07, 4.6910111910888134e-07, 2.841175273611667e-07, 1.6406085156799106e-07, 1.0378343343116844e-07, 5.2638957436288634e-08, 3.935467795709907e-08]
        
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

                elif row[0] == "female" :
                    female_age_key[age][0] += 1
                    avg_age_percentile[1] += 1
                    if row[3] != "alive" :
                        female_age_key[age][1] += 1
                        avg_mortality[1] += 1
        
        print(str(sum(avg_age_percentile)) + " out of " + str(len(self.patient_list)) + " are workable.")
        print(avg_age_percentile)
        print(avg_mortality)
        print(male_age_key)
        print(female_age_key)
        

        print(avg_age_percentile)
        print(avg_mortality)
        for i in range(self.maximum_age + 1) :
            if male_age_key[i][0] > 0 :
                male_age_key[i][0] = male_age_key[i][0]/demographic_data[i]
            else :
                male_age_key[i][0] = 0 

            if male_age_key[i][1] > 0 :
                male_age_key[i][1] = male_age_key[i][1]/demographic_data[i]
            else :
                male_age_key[i][1] = 0

            if female_age_key[i][0] > 0 :
                female_age_key[i][0] = female_age_key[i][0]/demographic_data[i]
            else :
                female_age_key[i][0] = 0

            if female_age_key[i][1] > 0 :
                female_age_key[i][1] = female_age_key[i][1]/demographic_data[i]
            else :
                female_age_key[i][1] = 0
        
        

        male_age_key = reject_outliers_double(male_age_key)
        female_age_key = reject_outliers_double(female_age_key)

        print(male_age_key)
        print(female_age_key)
        
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
                male_age_key = [[float(item) for item in row] for row in csv.reader(target)]
            with open(self.root_dir.replace("/", "\\") + "\\female_calculator_data.csv", "r", newline='') as target :
                female_age_key = [[float(item) for item in row] for row in csv.reader(target)]
            
            print("Done!")

        male_range = [[i for i in range(len(male_age_key))], [float(value[0]) for value in male_age_key]]
        female_range = [[i for i in range(len(female_age_key))], [float(value[0]) for value in female_age_key]]

        male_hosp_fit = np.poly1d(np.polyfit(male_range[0], male_range[1], 1))
        female_hosp_fit = np.poly1d(np.polyfit(female_range[0], female_range[1], 1))

        male_range = [[i for i in range(len(male_age_key))], [float(value[1]) for value in male_age_key]]
        female_range = [[i for i in range(len(female_age_key))], [float(value[1]) for value in female_age_key]]
    
        male_death_fit = np.poly1d(np.polyfit(male_range[0], male_range[1], 1))
        female_death_fit = np.poly1d(np.polyfit(female_range[0], female_range[1], 1))

        '''
        Just some code to plot a graph of the data

        xp = np.linspace(0, 120, 500)
        
        hosp = plt.figure(1)
        _ = plt.plot( xp, female_hosp_fit(xp), '-', xp, male_hosp_fit(xp), '--')
        plt.ylim([-1.5, 1.5])

        
        death = plt.figure(2)
        _ = plt.plot( xp, female_death_fit(xp), '-', xp, male_death_fit(xp), '--')
        plt.ylim([-1.5, 1.5])
        plt.draw()
        plt.clf()'''

        print("\nSaving regressed calculator key as csv in root dir...")
        
        regressed_male_age_key = [[float(male_hosp_fit(i)), float(male_death_fit(i))] for i in range(len(male_age_key))]
        regressed_female_age_key = [[float(female_hosp_fit(i)), float(female_death_fit(i))] for i in range(len(female_age_key))]

        highest_percentile = [max([i[0] for i in regressed_male_age_key]), max([i[0] for i in regressed_female_age_key])]

        highest_mortality = [max([i[1] for i in regressed_male_age_key]), max([i[1] for i in regressed_female_age_key])]

        avg_age_percentile = [100/i for i in highest_percentile]

        avg_mortality = [100/i for i in highest_mortality]        

        #Normalize to zero
        for i in range(self.maximum_age + 1) :
            regressed_male_age_key[i] = [regressed_male_age_key[i][0] * avg_age_percentile[0], regressed_male_age_key[i][1] * avg_mortality[0]]
            regressed_female_age_key[i] = [regressed_female_age_key[i][0] * avg_age_percentile[1], regressed_female_age_key[i][1] * avg_mortality[1]]

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
    #predictor.make_world_demographics()
    predictor.get_data_patients()
    male_age_key, female_age_key = predictor.build_calculator_data()
    clean_male_age_key, clean_female_age_key = predictor.build_regression_model()