import os.path
import csv
import pickle
from collections import OrderedDict

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.pyplot import figure
import random

class Manual:
    total_values = 8921484
    def __init__(self, file_loc):
        self.file_loc = file_loc
        self.analysis = dict()
        self.all_category_percentages = dict()

    def load(self):
        pickleFile = 'analysis.pickle'
        if os.path.isfile(pickleFile):
            with open(pickleFile, 'rb') as pickle_file:
                self.analysis = pickle.load(pickle_file)
            return
        with open(self.file_loc, encoding="utf8") as csvfile:
            readcsv = csv.reader(csvfile, delimiter=',')
            fieldTypes = None
            analysis_train = dict()
            analysis_train['0'] = dict()
            analysis_train['1'] = dict()

            analysis_test = []

            count = 0

            test_writer = csv.writer(open('test_data.csv', 'w+', encoding="utf8"))

            for row in readcsv:
                if fieldTypes == None:
                    fieldTypes = row
                    test_writer.writerow(fieldTypes)
                else:
                    if (count < Manual.total_values * .8):
                        for i in range(len(row) - 1):
                            hasVirus = row[len(row) - 1]
                            curField = fieldTypes[i]
                            curVal = row[i]
                            analysis_type = analysis_train[hasVirus]
                            if not curField in analysis_type:
                                analysis_type[curField] = dict()
                            if not curVal in analysis_type[curField]:
                                analysis_type[curField][curVal] = 0
                            analysis_type[curField][curVal] += 1
                    else:
                        test_writer.writerow(row)

                count += 1
            fileObject = open(pickleFile, 'wb')
            self.analysis['count'] = count
            self.analysis['test'] = analysis_test
            self.analysis['train'] = analysis_train
            pickle.dump(self.analysis, fileObject)

    def analyze_training_data(self):
        no_virus = self.analysis['train']['0']
        has_virus = self.analysis['train']['1']
        all_category_percentages = dict()
        for key in no_virus:
            if(self.valid_key(key)):
                all_category_percentages[key] = self.get_percentages(no_virus[key], has_virus[key])
        self.all_category_percentages = all_category_percentages

    def predict(self):
        with open('test_data.csv', encoding="utf8") as test_file:
            readcsv = csv.reader(test_file, delimiter=',')
            fields = None
            correct = 0
            incorrect = 0
            count = 0
            for row in readcsv:
                if fields == None:
                    fields = row
                    continue
                percentage = 0
                if not len(row) > 0:
                    continue

                correct_output = row[len(row) - 1]
                for i in range(len(row) - 1):
                    curField = fields[i]
                    if not self.valid_key(curField):
                        continue
                    curValue = row[i]
                    if curField in self.all_category_percentages and curValue in self.all_category_percentages[curField] and curValue != '':
                        percentage += self.all_category_percentages[curField][curValue]

                if percentage > 0:
                    predicted_output = '1'
                else:
                    predicted_output = '0'
                if predicted_output == correct_output:
                    correct += 1
                else:
                    incorrect += 1
                if count % 10000 == 0:
                    print('correct: ', correct)
                    print('incorrect ', incorrect)
                    print('percentage Correct: ', 100 * (correct / (correct + incorrect)))
                    print('count ', count)
                    print()
                count += 1
            print('Final correct: ', correct)
            print('Final incorrect: ', incorrect)
            print('Final Percentage Correct: ', 100 * (correct/(correct+incorrect)))

    def valid_key(self, key):
        ignore = {'MachineIdentifier', ''}
        return not key in ignore

    def get_percentages(self, no_virus_category: dict, has_virus_category: dict):
        percentage_sort = dict()
        for key in set().union(no_virus_category, has_virus_category):
            no_vir = no_virus_category[key] if key in no_virus_category else 0
            has_vir = has_virus_category[key] if key in has_virus_category else 0
            if(no_vir > has_vir):
                percentage_sort[key] =  -1 * (1 - (has_vir/no_vir))
            else:
                percentage_sort[key] = 1 - (no_vir/has_vir)
        percentage = OrderedDict(sorted(percentage_sort.items()))
        return percentage

    def graph_percentages(self):
        for field in self.all_category_percentages:
            if not self.valid_key(field):
                continue
            save_folder = 'figures'
            full_path = os.path.join(save_folder, field + '.png')
            if os.path.exists(full_path):
                print('Skipping', full_path, 'since it already exists.')
                continue

            all_labels = list(self.all_category_percentages[field].keys())
            all_vals = list(self.all_category_percentages[field].values())

            print(field, 'size is', len(all_labels))


            plt.rcdefaults()
            fig, ax = plt.subplots()

            y_pos = np.arange(len(all_labels))

            for i, val in enumerate(all_vals):
                if val < 0:
                    color = 'green'
                else:
                    color = 'red'
                ax.barh([i], val * -1, color=color, align='center')

            ax.figure.set_size_inches(15, len(all_labels) * .2 + 5)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(all_labels)
            ax.invert_yaxis()
            ax.set_xlabel('Has Virus Percent <-- 0 --> No Virus Percent ')
            ax.set_xlim([-1, 1])
            ax.set_title(field)

            if not os.path.exists(save_folder):
                os.mkdir(save_folder)

            plt.savefig(full_path)
            plt.close()

def main():
    manual = Manual(os.path.join('..', 'microsoft-malware-prediction', 'train.csv'))
    manual.load()
    manual.analyze_training_data()
    manual.graph_percentages()
    manual.predict()

if __name__ == "__main__":
    main()