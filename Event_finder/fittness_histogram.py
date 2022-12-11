import numpy as np
import json
import matplotlib.pyplot as plt



def create_histogram(
    fitness_dictionary_file,
):
    with open(fitness_dictionary_file, 'r') as openfile:
        fitness_dictionary = json.load(openfile)

    fitness_array = []
    for i in fitness_dictionary:
        for j in fitness_dictionary[i]:
            fitness_array.append(j[0])

    fitness_histogram = np.histogram(fitness_array,bins=1000,range=(300000,1000000))
    return fitness_histogram
    fig, axs = plt.subplots()
    axs.bar(fitness_histogram[1][1:],fitness_histogram[0])
    plt.show()
    