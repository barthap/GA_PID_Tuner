import os
import tkinter as tk
from datetime import datetime
from threading import Thread
from tkinter import ttk, messagebox

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D     # do not remove, it is actually necessary

import listtools
from config import config as default_cfg
from genetic.algorithms.impl1 import GeneticAlgorithmImpl
from genetic.simulation import Simulation
from sim.PythonSimulatedModel import PythonSimulatedModel

LARGE_FONT=("Arial Bold", 18)
TITLE_FONT=("Arial Bold", 20)
SUBTITLE_FONT=("Arial Bold", 16)


# Current simulation state
class SimulationStatus():
    def __init__(self):
        self.champion_chromosomes = []
        self.max_values = []
        self.avg_values = []
        self.stds = []
        self.totalTime = 0.0
        self.current_population = None
        self.running = False
        self.drawEvent = False
        self.kill = False


# Main app class
class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # maximizes window
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        self.geometry("{}x{}+0+0".format(w, h))

        tk.Tk.wm_title(self, "GA PID Tuner")

        self.bind("<Escape>", lambda e: e.widget.quit())

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.container = container

        self.frames = {}
        self.global_params = {}

        self.fig = Figure(figsize=(12, 5), dpi=100)
        self.ax = self.fig.add_subplot(121, projection='3d')
        self.ax2 = self.fig.add_subplot(122, projection='3d')

        self.reset_frames(frames=(SettingsPage,ProgressPage,ResultsPage))
        self.show_frame(SettingsPage)

    def reset_frames(self, frames):
        # lista ekranów możliwych do wyświetlenia
        for F in frames:
            frame = F(self.container, self)
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

    # wyświetla dany ekran
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.do_show()
        frame.tkraise()

    def init_3d_plot(self, config):
        self.ax2.set_xlim(0, config['max_gain_value'])
        self.ax2.set_ylim(0, config['max_integral_value'])
        self.ax2.set_zlim(0, config['max_derivative_value'])
        self.ax2.set_xlabel("Kp")
        self.ax2.set_ylabel("Ti")
        self.ax2.set_zlabel("Td")
        self.ax.clear()
        self.ax2.clear()
        self.ax2.set_title("Previous generations")
        self.ax.set_title("Current generation")

    # aktualizuje wykres 3D
    def update_animation(self):
        status = self.global_params['status']
        cfg = self.global_params['cfg']
        if status.current_population is not None and status.running is True:
            population = status.current_population
            ax = self.ax
            ax2 = self.ax2
            kps = [x.kp for x in population]
            Tis = [x.Ti for x in population]
            Tds = [x.Td for x in population]
            ax.clear()
            ax.set_xlim(0, cfg['max_gain_value'])
            ax.set_ylim(0, cfg['max_integral_value'])
            ax.set_zlim(0, cfg['max_derivative_value'])
            ax.set_title("Current generation")
            ax.scatter(kps, Tis, Tds)
            ax2.scatter(kps, Tis, Tds)
            ax.set_xlabel("Kp")
            ax.set_ylabel("Ti")
            ax.set_zlabel("Td")


# Ekran ustawień
class SettingsPage(tk.Frame):
    def __init__(self, parent, controller: Application):
        tk.Frame.__init__(self,parent)

        self.config = default_cfg
        self.controller = controller

        self.grid_columnconfigure(0, weight=1, uniform="group2")
        self.grid_columnconfigure(1, weight=1, uniform="group2")

        tk.Label(self, text="Settings", font=TITLE_FONT).grid(row=0,sticky='nswe', columnspan=2)

        tk.Label(self, text="PID Simulation Settings", font=SUBTITLE_FONT).grid(row=2,sticky='nswe', columnspan=2,
                                                                                 pady=(5, 0))
        tk.Label(self, text="Integration step [s]").grid(row=3, sticky='e')
        tk.Label(self, text="Simulation time [s]").grid(row=4, sticky='e')
        tk.Label(self, text="Pade approx. level").grid(row=5, sticky='e')
        tk.Label(self, text="Derivative innertion time constant").grid(row=6, sticky='e')
        tk.Label(self, text="Transfer fn. numerator").grid(row=7, sticky='e')
        tk.Label(self, text="Transfer fn. denominator").grid(row=8, sticky='e')
        tk.Label(self, text="Transfer delay [s]").grid(row=9, sticky='e')

        tk.Label(self, text="Genetic Algorithm Settings", font=SUBTITLE_FONT).grid(row=12, sticky='swe', columnspan=2,
                                                                                          pady=(5, 0))
        tk.Label(self, text="Population size").grid(row=13,sticky='e')
        tk.Label(self, text="Number of generations").grid(row=14,sticky='e')
        tk.Label(self, text='Max k').grid(row=15,sticky='e')
        tk.Label(self, text='Max Ti').grid(row=16,sticky='e')
        tk.Label(self, text='Max Td').grid(row=17,sticky='e')
        tk.Label(self, text="Mutation probability").grid(row=18,sticky='e')
        tk.Label(self, text="Crossover rate").grid(row=19,sticky='e')

        self.step_time = tk.Entry(self, width=5)
        self.step_time.grid(row=3, column=1, sticky='w')
        self.step_time.insert(tk.END, str(default_cfg['step_time']))
        self.simulation_time = tk.Entry(self, width=5)
        self.simulation_time.grid(row=4, column=1, sticky='w')
        self.simulation_time.insert(tk.END, str(default_cfg['simulation_time']))
        self.pade_N = tk.Entry(self, width=5)
        self.pade_N.grid(row=5, column=1, sticky='w')
        self.pade_N.insert(tk.END, str(default_cfg['pade_N']))
        self.D_T = tk.Entry(self, width=5)
        self.D_T.grid(row=6, column=1, sticky='w')
        self.D_T.insert(tk.END, str(default_cfg['D_T']))
        self.tf_num = tk.Entry(self, width=5)
        self.tf_num.grid(row=7, column=1, sticky='w')
        self.tf_num.insert(tk.END, str(default_cfg['tf_num']).replace("[", "").replace("]", ""))
        self.tf_den = tk.Entry(self, width=5)
        self.tf_den.grid(row=8, column=1, sticky='w')
        self.tf_den.insert(tk.END, str(default_cfg['tf_den']).replace("[", "").replace("]", ""))
        self.delay = tk.Entry(self, width=5)
        self.delay.grid(row=9, column=1, sticky='w')
        self.delay.insert(tk.END, str(default_cfg['delay']))

        self.population_size = tk.Entry(self, width=5)
        self.population_size.grid(row=13, column=1, sticky='w')
        self.population_size.insert(tk.END, str(default_cfg['population_size']))
        self.max_runs = tk.Entry(self, width=5)
        self.max_runs.grid(row=14, column=1, sticky='w')
        self.max_runs.insert(tk.END, str(default_cfg['max_runs']))
        self.max_gain_value = tk.Entry(self, width=5)
        self.max_gain_value.grid(row=15, column=1, sticky='w')
        self.max_gain_value.insert(tk.END, str(default_cfg['max_gain_value']))
        self.max_integral_value = tk.Entry(self, width=5)
        self.max_integral_value.grid(row=16, column=1, sticky='w')
        self.max_integral_value.insert(tk.END, str(default_cfg['max_integral_value']))
        self.max_derivative_value = tk.Entry(self, width=5)
        self.max_derivative_value.grid(row=17, column=1, sticky='w')
        self.max_derivative_value.insert(tk.END, str(default_cfg['max_derivative_value']))
        self.mutation_probability = tk.Entry(self, width=5)
        self.mutation_probability.grid(row=18, column=1, sticky='w')
        self.mutation_probability.insert(tk.END, str(default_cfg['mutation_probability']))
        self.crossover_rate = tk.Entry(self, width=5)
        self.crossover_rate.grid(row=19, column=1, sticky='w')
        self.crossover_rate.insert(tk.END, str(default_cfg['crossover_rate']))

        self.start_btn = tk.Button(self, text="Start", width = 20, height = 3, command=self.start_simulation)
        self.start_btn.grid(row=23, column=0, sticky='e')

        self.close = tk.Button(self, text="Close", width = 20, height = 3, command=self.controller.destroy)
        self.close.grid(row=23, column=1, sticky='w')

    def do_show(self):
        pass

    def accept_parameters(self):
        if self.population_size.get() :
            self.config['population_size']=int(self.population_size.get())
        if self.max_runs.get():
            self.config['max_runs']=int(self.max_runs.get())
        if self.max_gain_value.get() :
            self.config['max_gain_value']=float(self.max_gain_value.get())
        if self.max_integral_value.get():
            self.config['max_integral_value']=float(self.max_integral_value.get())
        if self.max_derivative_value.get() :
            self.config['max_derivative_value']=float(self.max_derivative_value.get())
        if self.mutation_probability.get() :
            self.config['mutation_probability']=float(self.mutation_probability.get())
        if self.crossover_rate.get():
            self.config['crossover_rate']=float(self.crossover_rate.get())
        if self.step_time.get() :
            self.config['step_time']=float(self.step_time.get())
        if self.simulation_time.get():
            self.config['simulation_time']=float(self.simulation_time.get())
        if self.pade_N.get() :
            self.config['pade_N']=int(self.pade_N.get())
        if self.D_T.get():
            self.config['D_T']=float(self.D_T.get())
        if self.tf_num.get():
            x = self.tf_num.get().replace(" ", "").split(",")
            for i in range(len(x)):
                x[i]=float(x[i])
            self.config["tf_num"] = x
        if self.tf_den.get():
            x = self.tf_den.get().replace(" ", "").split(",")
            for i in range(len(x)):
                x[i]=float(x[i])
            self.config['tf_den'] = x
        if self.delay.get() :
            self.config['delay']=float(self.delay.get())

        self.controller.global_params['cfg'] = self.config
        print("parametry zatwierdzono")

    def start_simulation(self):
        self.accept_parameters()
        self.controller.reset_frames((ProgressPage, ResultsPage))
        self.controller.init_3d_plot(self.config)
        self.controller.show_frame(ProgressPage)


# Ekran z postępem
class ProgressPage(tk.Frame):
    def __init__(self, parent, controller: Application):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.simulation = None
        self.thread: Thread = None
        self.canvas = None

        self.label = tk.Label(self, text="Starting simulation...", font=LARGE_FONT)
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, maximum=100, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=20)

        self.cancel_btn = tk.Button(self, text="Cancel", width=20, height=2,
                                    command=self.cancel)
        self.cancel_btn.pack(pady=10)

    def cancel(self):
        self.controller.global_params['status'].kill = True
        self.after(50, self.cancel_tick)

    def cancel_tick(self):
        if self.thread.isAlive():
            self.after(50, self.cancel_tick)
        else:
            self.controller.reset_frames((ProgressPage, ResultsPage))
            self.controller.show_frame(SettingsPage)

    def update_label(self, i, max, avg, std):
        max_runs = self.controller.global_params['cfg']['max_runs']
        self.progress_bar['value'] = (i / max_runs * 100)

        txt = "Generation {}:\tBest: {:.4f}\tAvg: {:.4f}\tStd: {:.4f}".format(i + 1, max, avg, std)
        self.label['text']=txt

    # To sie wywołuje po kliknięciu przycisku start
    def do_show(self):
        cfg = self.controller.global_params['cfg']
        self.simulation = Simulation(cfg,
                                     PythonSimulatedModel(cfg),
                                     GeneticAlgorithmImpl(cfg))

        self.controller.global_params['sim'] = self.simulation
        self.controller.global_params['status'] = SimulationStatus()

        canvas = FigureCanvasTkAgg(self.controller.fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas = canvas

        # Uruchom wątek w tle z algorytmem
        self.thread = Thread(target=self.run_sim)
        self.thread.start()

        self.after(100, self.check_thread)

    # Aktualizuje GUI na podstawie postępu algorytmu w tle
    def check_thread(self):
        if self.thread.isAlive():
            status = self.controller.global_params['status']
            if status.drawEvent is True:
                self.controller.update_animation()
                self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
                self.canvas.draw()
                status.drawEvent = False
            self.after(100, self.check_thread)
        else:
            self.thread.join()
            if not self.controller.global_params['status'].kill:
                self.after(0, lambda: self.controller.show_frame(ResultsPage))

    # Ta funkcja wywołuje się w osobnym watku (w tle) żeby nie blokować GUI
    def run_sim(self):
        simulation = self.simulation
        cfg = self.controller.global_params['cfg']
        MAX_RUNS = cfg['max_runs']
        status: SimulationStatus = self.controller.global_params['status']
        status.running = True

        dt_start = datetime.timestamp(datetime.now())

        simulation.generate_initial_population()

        # symulujemy kolejne iteracje, zapisując wyniki każdej z nich
        for i in range(MAX_RUNS):

            if status.kill is True:
                #status.running = False
                return

            # populacja i fitness z aktualnego pokolenia
            population = simulation.population
            fitness_values = simulation.fitness_values

            # może już przetwarzać sobie następne, jeśli to nie było ostatnie
            if i < MAX_RUNS - 1:
                simulation.next_generation()

            std = np.std(fitness_values)

            # add the champion chromosome to a list of champions for plotting
            index_of_champion = listtools.max_index_in_list(fitness_values)
            status.champion_chromosomes.append(population[index_of_champion])

            # add the max/average values to lists for plotting
            status.max_values.append(listtools.max_value_in_list(fitness_values))
            status.avg_values.append(listtools.avgList(fitness_values))
            status.stds.append(std)

            status.current_population = population
            status.drawEvent = True
            status.iteration = i
            self.after(0, self.update_label(i, status.max_values[i], status.avg_values[i], std))

            if status.kill is True:
                #status.running = False
                return

        dt_end = datetime.timestamp(datetime.now())
        status.totalTime = dt_end - dt_start

        status.running = False

# Ekran z wynikami
class ResultsPage(tk.Frame):
    # Konstruktor sie wywołuje zaraz po uruchomieniu aplikacji
    def __init__(self, parent, controller: Application):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=6, uniform="group1")
        self.grid_rowconfigure(1, weight=6, uniform="group1")
        self.grid_rowconfigure(2, weight=1, uniform="group1")
        self.grid_rowconfigure(3, weight=1, uniform="group1")
        self.grid_rowconfigure(4, weight=1, uniform="group1")
        self.grid_rowconfigure(5, weight=1, uniform="group1")
        self.grid_rowconfigure(6, weight=1, uniform="group1")
        self.grid_rowconfigure(7, weight=1, uniform="group1")
        self.grid_columnconfigure(0, weight=1, uniform="group2")
        self.grid_columnconfigure(1, weight=1, uniform="group2")

        self.return_ = tk.Button(self, text="New simulation", width=20, height=2,
                                 command=lambda: self.controller.show_frame(SettingsPage))
        self.return_.grid(row=4, column=1, sticky="n", pady=(0,10))

        self.save_btn = tk.Button(self, text="Save plots", width=20, height=2,
                                  command=self.save)
        self.save_btn.grid(row=5, column=1, sticky="n", pady=(0,10))

        self.close = tk.Button(self, text="Finish", width = 20, height=2,
                               command=self.controller.destroy)
        self.close.grid(row=6, column=1, sticky="n",rowspan=2)

        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.p4 = None

    def save(self):
        now = datetime.now()
        cfg = self.controller.global_params['cfg']
        fname = "sim_" + now.strftime("%d-%m-%Y_%H.%M.%S") + "_" + str(cfg['max_runs']) + "_" + str(cfg['population_size']) + "_"

        if not os.path.exists('Saves'):
            os.makedirs('Saves')
        self.p1.savefig(os.path.join('Saves', fname + 'fitness.png'))
        self.p2.savefig(os.path.join('Saves', fname + 'values.png'))
        self.p3.savefig(os.path.join('Saves', fname + 'response.png'))
        self.p4.savefig(os.path.join('Saves', fname + 'std.png'))

        messagebox.showinfo("Saved successfully!", "Plots have been saved in " + os.path.abspath('Saves'))

    # To sie wywołuje jak ekran się zaczyna wyświetlać (dopiero po zakończeniu algorytmu)
    def do_show(self):
        results: SimulationStatus = self.controller.global_params['status']
        cfg = self.controller.global_params['cfg']
        MAX_RUNS = cfg['max_runs']

        tk.Label(self, text="Algorithm total time: {:.2f}s".format(results.totalTime)).grid(row=2, column=0, sticky='w')

        best_index = listtools.max_index_in_list(results.max_values)
        best_chromosome = results.champion_chromosomes[best_index]
        tk.Label(self,
                 text="Starting result: {:.4f}, Starting values: "
                 .format(results.max_values[0]) + str(results.champion_chromosomes[0]))\
            .grid(row=3, column=0, sticky='w')
        tk.Label(self, text="Best generation: " + str(best_index + 1)).grid(row=4, column=0, sticky='sw')
        tk.Label(self, text="Best result: {:.4f}, Reduced ISE: {:.4f}"
                 .format(results.max_values[best_index], 1.0 / results.max_values[best_index]))\
            .grid(row=5, column=0, sticky='nw')
        tk.Label(self, text="Calculated PID values: " + str(best_chromosome)).grid(row=6, column=0, sticky='sw')

        tk.Label(self, text="Population size: {}\t Generations count: {}".format(cfg['population_size'], cfg['max_runs']))\
            .grid(row=3, column=1,sticky='we')

        p = plt.figure()
        canvas = FigureCanvasTkAgg(p, self)
        canvas.get_tk_widget().grid(row=0, column=0, sticky="we")

        plt.title("Generation fitness value")
        plt.plot(range(1,MAX_RUNS+1), results.max_values, marker='.', label=r"Best")
        plt.plot(range(1,MAX_RUNS+1), results.avg_values, marker='.', label=r"Average")
        plt.plot([best_index+1], results.max_values[best_index], marker='o', color='r')
        plt.legend(loc='lower right')
        plt.grid()
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.tight_layout()
        plt.gcf().subplots_adjust(bottom=0.3)
        self.p1 = p

        # plot values of parameters for each run
        # plt.subplot(2,1,2)
        p2 = plt.figure()
        canvas2 = FigureCanvasTkAgg(p2, self)
        canvas2.get_tk_widget().grid(row=0, column=1, sticky="we")

        plt.title("Generation best PID values")
        plt.plot(range(1,MAX_RUNS+1), [x.kp for x in results.champion_chromosomes], marker='.', label=r"Kp")
        plt.plot(range(1,MAX_RUNS+1), [x.Ti for x in results.champion_chromosomes], marker='.', label=r"Ti")
        plt.plot(range(1,MAX_RUNS+1), [x.Td for x in results.champion_chromosomes], marker='.', label=r"Td")
        plt.legend(loc='center right')
        plt.grid()
        plt.xlabel("Generation")
        plt.ylabel("Value")
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.3)
        self.p2 = p2

        fit, t, y = self.controller.global_params['sim'].sim_model.simulate_for_fitness(best_chromosome)

        tk.Label(self, text="Integral Square Error (ISE): {:.4f}".format(fit)).grid(row=7, column=0, sticky='nw')
        p3 = plt.figure(figsize=(6.4, 3.6))
        canvas3 = FigureCanvasTkAgg(p3, self)
        canvas3.get_tk_widget().grid(row=1, column=0, sticky="we")
        plt.plot(t, y, 'b')
        plt.xlabel('t [s]')
        plt.ylabel('Step response')
        plt.grid(True)
        plt.title('PID tuning result')
        plt.tight_layout()
        plt.gcf().subplots_adjust(bottom=0.25)
        self.p3 = p3


        p4 = plt.figure(figsize=(6.4, 2.4))
        canvas4 = FigureCanvasTkAgg(p4, self)
        canvas4.get_tk_widget().grid(row=1, column=1, sticky="wens")
        plt.plot(range(MAX_RUNS), results.stds)
        plt.title("Fitness standard deviation")
        plt.grid()
        plt.xlabel("Generation")
        plt.tight_layout()
        self.p4 = p4

        dummy = plt.figure()
        new_manager = dummy.canvas.manager
        # create a dummy figure and use its
        new_manager.canvas.figure = p4
        p4.set_canvas(new_manager.canvas)
