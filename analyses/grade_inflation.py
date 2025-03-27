import json
import os
from pathlib import Path
import re
import numpy
import matplotlib.pyplot as plt

course = []
with open('results.json', 'r') as f:
    text = f.read()
    courses = json.loads(text)

course_types = set()
for course in courses:
    for i in range(len(course['course'])):
        if course['course'][i] == ' ':
            course_types.add(course['course'][:i])
            break

data = {course: [[] for i in range(74)] for course in course_types}

def clean():
    for course in courses:
        for i in range(len(course['course'])):
            if course['course'][i] == ' ':
                course['course'] = course['course'][:i]
                break
        if '/' in course['avg grade recieved']:
            courses.remove(course)
            continue
        else:
            match = re.search(r'(\d+\.\d+)', course['avg grade recieved'])
            course['avg grade recieved']= float(match.group(1)) if match else None
            if course['avg grade recieved'] == None:
                courses.remove(course)
                continue
        season_map = {'S1': 0, 'SU': 0, 'S3': 0, 'S2': 0, 'FA': 1, 'WI': 2, 'SP': 3}
        if len(course['term']) < 4:
            courses.remove(course)
        else:
            time = (int(course['term'][2:])-7)*4 + season_map[course['term'][:2]]
            #print(course['term'], time)
            data[course['course']][time].append(course['avg grade recieved'])

def plot_course_gpas(course_data):
    plt.figure(figsize=(15, 8))

    #quarters = ['07', '07', '07','07', '08', '08', '08', '08', '09', '09', '09', '09', '10', '10', '10', '10', '11', '11', '11', '11', '12', '12', '12', '12', '13', '13', '13', '13', '14', '14', '14', '14', '15', '15', '15', '15', '16', '16', '16', '16', '17', '17', '17', '17', '18', '18', '18', '18', '19', '19', '19', '19', '20', '20', '20', '20', '21', '21', '21', '21', '22', '22', '22', '22' '23', '23', '23', '23', '24', '24', '24', '24', '25', '25']
    for course, gpas in course_data.items():

        x_values = []
        y_values = []
        

        for i, gpa in enumerate(gpas):
            if gpa != 0:
                x_values.append(i)
                y_values.append(gpa)
        

        plt.plot(x_values, y_values, marker='o', linestyle='-', label=course)
    

    plt.title('Average Course GPAs Over Time', fontsize=16)
    plt.xlabel('Time Period', fontsize=12)
    plt.ylabel('Average GPA', fontsize=12)
    plt.legend(title='Courses')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Show the plot
    plt.tight_layout()
    plt.show()

def main():
    clean()
    for d in course_types:
        for i in range(74):
            if len(data[d][i]) > 0:
                data[d][i] = sum(data[d][i])/len(data[d][i])
            else:
                data[d][i] = 0
    plot_course_gpas({course : data[course] for course in {'MAE', 'ECE', 'MATH', 'PHYS', 'BILD','CSE', 'COGS', 'SE', 'PSYC'}})





main() 

