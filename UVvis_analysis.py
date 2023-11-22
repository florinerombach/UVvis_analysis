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

    # Read list of all samples and label transmittance and reflectance measurements
    with open(data_path,'r') as file:
        reader = csv.reader(file, delimiter=',')
        data = list(reader)

    measurements = [m for m in data[0][::2] if m != ''] 
    meas_type = [t[-1] for t in data[1][1::2] if t != '']

    samples = [m for (m,t) in list(zip(measurements, meas_type)) if t == 'T' and 'Baseline' not in m]

    for i, _ in enumerate(measurements):
        if meas_type[i] == 'T':
            measurements[i] = measurements[i] + '_T'
        elif meas_type[i] == 'R':
            measurements[i] = measurements[i] + '_R'

    # Import data for each measurement
    d = defaultdict(list)
    for row in data:
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
    
    if not os.path.isdir(os.path.join(save_path,f'T_R_indv_plots')):
        os.mkdir(os.path.join(save_path,f'T_R_indv_plots'))

    for s in samples:
        # test that wavelength ranges measured are the same:
        if [i for i, j in d[s+'_T']] == [i for i, j in d[s+'_R']]:

            E = 1240/np.array([i for i, j in d[s+'_T']])
            energy_dict[s] = E
            T = np.array([j for i, j in d[s+'_T']])/100
            R = np.array([j for i, j in d[s+'_R']])/100

            # Plot individual transmittance/reflectance
            plt.plot(E, T, label = 'transmittance')
            plt.plot(E, R, label = 'reflectance')
            plt.xlim(E[0], E[-1])
            plt.ylim(0, 1)
            plt.xlabel('Energy (eV)', fontsize=14)
            plt.ylabel('Transmittance / Reflectance', fontsize=14)
            plt.legend()
            plt.savefig(os.path.join(save_path,f'T_R_indv_plots',f'{s}.png'), format='png',dpi=300)
            plt.clf()

            # Calculate absorptance, absorbance, absorbance coefficient
            try:
                absorptance = 1 - T - R
                absorbance = -np.log(T+R)

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
    
    # Plot all transmittance in one graph
    for s in samples_cut:
        E = energy_dict[s]
        T = np.array([j for i, j in d[s+'_T']])/100
        plt.plot(E, T, label = s)
    plt.xlim(min([energy_dict[s][0] for s in samples_cut]), max([energy_dict[s][-1] for s in samples_cut]))
    plt.ylim(0, 1)
    plt.xlabel('Energy (eV)', fontsize=14)
    plt.ylabel('Transmittance', fontsize=14)
    plt.legend()
    plt.savefig(os.path.join(save_path,f'T_R_indv_plots',f'all_transmittance.png'), format='png',dpi=300)
    plt.clf()

    # Plot all reflectance in one graph
    for s in samples_cut:
        E = energy_dict[s]
        R = np.array([j for i, j in d[s+'_R']])/100
        plt.plot(E, R, label = s)
    plt.xlim(min([energy_dict[s][0] for s in samples_cut]), max([energy_dict[s][-1] for s in samples_cut]))
    plt.ylim(0, 1)
    plt.xlabel('Energy (eV)', fontsize=14)
    plt.ylabel('Reflectance', fontsize=14)
    plt.legend()
    plt.savefig(os.path.join(save_path,f'T_R_indv_plots',f'all_reflectance.png'), format='png',dpi=300)
    plt.clf()

    print('Analysed samples: ', ', '.join(samples_cut)) 

    return samples_cut, energy_dict, absorptance_dict, absorbance_dict, alpha_dict


def export_data(save_path, thickness, samples_cut, energy_dict, absorptance_dict, absorbance_dict, alpha_dict):
    
    # Export calculated absorption values to csv
    if thickness != None:
        quants =  [('absorptance', absorptance_dict), ('absorbance', absorbance_dict), ('alpha', alpha_dict)]
    else:
        quants =  [('absorptance', absorptance_dict), ('absorbance', absorbance_dict)]

    for measurement, dict in quants:

        with open(os.path.join(save_path,f'{measurement}.csv'), 'w', newline='') as csvfile:

            writer = csv.writer(csvfile, delimiter=',')
            headings = [('Energy (eV)', 'Sample '+ s) for s in samples_cut]
            headings = np.array(headings).flatten()

            writer.writerow(headings)

            for i in range(len(energy_dict[samples_cut[0]])):
                row = []
                for s in samples_cut:
                    row.extend(('{:.3f}'.format(energy_dict[s][i]), '{:.3f}'.format(dict[s][i])))
                writer.writerow(row)

    # Plot absorptance for all samples
    for s in samples_cut:
        try:
            plt.plot(energy_dict[s], absorptance_dict[s], label = s)
        except:
            continue
    plt.legend()
    plt.xlim(min([energy_dict[s][0] for s in samples_cut]), max([energy_dict[s][-1] for s in samples_cut]))
    plt.ylim(0, 1)
    plt.xlabel('Energy (eV)', fontsize=14)
    plt.ylabel('Absorptance', fontsize=14)
    plt.savefig(os.path.join(save_path,'absorptance.png'), format='png',dpi=300)
    plt.clf()

    # Plot absorbance for all samples
    for s in samples_cut:
        try:
            plt.plot(energy_dict[s], absorbance_dict[s], label = s)
        except:
            continue
    plt.legend()
    plt.xlim(min([energy_dict[s][0] for s in samples_cut]), max([energy_dict[s][-1] for s in samples_cut]))
    plt.ylim(ymin = 0)
    plt.xlabel('Energy (eV)', fontsize=14)
    plt.ylabel('Absorbance', fontsize=14)
    plt.savefig(os.path.join(save_path,'absorbance.png'), format='png',dpi=300)
    plt.clf()

    # Plot absorbance coefficient for all samples, if film thickness is provided
    if thickness != None:
        for s in samples_cut:
            try:
                plt.plot(energy_dict[s],alpha_dict[s], label = s)
            except:
                continue
        plt.legend()
        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
        plt.xlabel('Energy (eV)', fontsize=14)
        plt.ylabel('Absorbance coefficient (cm^-1)', fontsize=14)
        plt.xlim(min([energy_dict[s][0] for s in samples_cut]), max([energy_dict[s][-1] for s in samples_cut]))
        plt.yscale('log')
        plt.savefig(os.path.join(save_path,'alpha.png'), format='png',dpi=300)
        plt.clf()


def main():

    args = get_args()
    save_path = os.path.join(os.path.dirname(args.data_path), 'processed')
    if not os.path.isdir(save_path):
        os.mkdir(save_path)
    samples, d = read_data(args.data_path)
    samples_cut, energy_dict, absorptance_dict, absorbance_dict, alpha_dict = analyse_data(samples, d, args.thickness, save_path)
    export_data(save_path, args.thickness, samples_cut, energy_dict, absorptance_dict, absorbance_dict, alpha_dict)


if __name__ == "__main__":
    main()