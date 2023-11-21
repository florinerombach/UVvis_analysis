import csv
import os
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from gooey import Gooey, GooeyParser

@Gooey()

def get_args():
    parser = GooeyParser(description='Process transmittance and reflectance data.')

    parser.add_argument(
        "-d",
        "--data_path",
        metavar="Data Path",
        help="Select .csv file containing all T, R measurements.",
        widget="FileChooser",
        gooey_options=dict(wildcard="*.csv"),
        required=True
    )

    parser.add_argument(
        "-t",
        "--thickness",
        metavar='Film Thickness',
        help="Enter film thickness in nm, if same for all samples. If blank, absorbance coefficient won't be calculated.",
        type=float,
        required=False)  

    args = parser.parse_args()

    return args

def read_data(data_path):

    d = defaultdict(list)

    with open(data_path,'r') as file:

        reader = csv.reader(file, delimiter=',')
        measurements = (list(reader))[0][::2] 

        baseline_indexes = [i for i, elem in enumerate(measurements) if 'Baseline' in elem]
        diffs = [t - s for s, t in zip(baseline_indexes,baseline_indexes[1:])]
        reflectance_start = [i+1 for i, elem in enumerate(diffs) if elem > 2]
        if len(reflectance_start) > 1:
            print('WARNING: Input data formatting error.')
        reflectance_start_index = baseline_indexes[reflectance_start[0]]

        samples = [s for s in measurements[:reflectance_start_index] if 'Baseline' not in s]
        print('Analysing samples: ', ', '.join(samples)) 

        for i, _ in enumerate(measurements):
            if i < reflectance_start_index:
                measurements[i] = measurements[i] + '_T'
            elif i >= reflectance_start_index:
                measurements[i] = measurements[i] + '_R'


    with open(data_path,'r') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            for j, m in enumerate(measurements):
                try:
                    datapoint = (float(row[2*j]), float(row[2*j+1]))
                    d[m].append(datapoint)
                except:
                    continue

    return samples, d


def analyse_data(samples, d, thickness, save_path):

    absorptance_dict = {}
    absorbance_dict = {}
    alpha_dict = {}
    energy_dict = {}
    samples_cut = []

    for s in samples:
        # test that wavelength ranges measured are the same:
        if [i for i, j in d[s+'_T']] == [i for i, j in d[s+'_R']]:

            E = 1240/np.array([i for i, j in d[s+'_T']])
            energy_dict[s] = E
            T = np.array([j for i, j in d[s+'_T']])/100
            R = np.array([j for i, j in d[s+'_R']])/100

            plt.plot(E, T, label = 'transmittance')
            plt.plot(E, R, label = 'reflectance')
            plt.legend()
            plt.savefig(save_path+f'/T_R_{s}.png', format='png',dpi=300)
            plt.clf()

            try:
                absorptance = 1 - T - R
                absorbance = -np.log(1-absorptance)

                absorptance_dict[s] = absorptance
                absorbance_dict[s] = absorbance

                if thickness != None:
                    alpha = absorbance/(thickness*1e-7)
                    alpha_dict[s] = alpha

                samples_cut.append(s)

            except:
                print('Sample ', s, ': Invalid value encountered in calculations - check your data.')
        else:
            print('Sample ', s, ": T and R measurements are missing or don't match up - check your data.")

    return samples_cut, energy_dict, absorptance_dict, absorbance_dict, alpha_dict


def export_data(save_path, thickness, samples_cut, energy_dict, absorptance_dict, absorbance_dict, alpha_dict):
        
    if thickness != None:
        quants =  [('absorptance', absorptance_dict), ('absorbance', absorbance_dict), ('alpha', alpha_dict)]
    else:
        quants =  [('absorptance', absorptance_dict), ('absorbance', absorbance_dict)]

    for measurement, dict in quants:

        with open(save_path+f'\{measurement}.csv', 'w', newline='') as csvfile:

            writer = csv.writer(csvfile, delimiter=',')
            headings = [('Energy (eV)', 'Sample '+ s) for s in samples_cut]
            headings = np.array(headings).flatten()

            writer.writerow(headings)

            for i in range(len(energy_dict[samples_cut[0]])):
                row = []
                for s in samples_cut:
                    row.extend(('{:.3f}'.format(energy_dict[s][i]), '{:.3f}'.format(dict[s][i])))
                writer.writerow(row)

    plt.title('Absorptance')
    for s in samples_cut:
        print()
        try:
            plt.plot(energy_dict[s], absorptance_dict[s], label = s)
        except:
            continue
    plt.legend()
    plt.savefig(save_path+f'/absorptance.png', format='png',dpi=300)
    plt.clf()

    plt.title('Absorbance')
    for s in samples_cut:
        try:
            plt.plot(energy_dict[s], absorbance_dict[s], label = s)
        except:
            continue
    plt.legend()
    plt.savefig(save_path+f'/absorbance.png', format='png',dpi=300)
    plt.clf()

    if thickness != None:
        plt.title('Absorbance coefficient')
        for s in samples_cut:
            try:
                plt.plot(energy_dict[s],alpha_dict[s], label = s)
            except:
                continue
        plt.legend()
        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
        plt.savefig(save_path+f'/alpha.png', format='png',dpi=300)
        plt.yscale('log')
        plt.clf()

def main():

    args = get_args()
    save_path = os.path.dirname(args.data_path)
    print(save_path)
    samples, d = read_data(args.data_path)
    samples_cut, energy_dict, absorptance_dict, absorbance_dict, alpha_dict = analyse_data(samples, d, args.thickness, save_path)
    export_data(save_path, args.thickness, samples_cut, energy_dict, absorptance_dict, absorbance_dict, alpha_dict)

if __name__ == "__main__":
    main()