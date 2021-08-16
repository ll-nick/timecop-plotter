import os
import logging
import argparse
import csv
import datetime
import matplotlib.pyplot as plt

class Timer:
    def __init__(self, date, project, description, start, end, duration, notes):
        m, d, y = date.split("/")
        self.date = datetime.date(int(y), int(m), int(d))
        self.project = project
        self.main_project = self.classify_project(project)
        self.description = description
        self.start = self.process_time_str(start)
        self.end = self.process_time_str(end)
        self.duration = float(duration)
        self.notes = notes

    def classify_project(self, project):
        if project == "Abschlussarbeiter" or \
            project == "GMRT" or \
            project == "KAL" or \
            project == "KSOP" or \
            project == "MTP/RVMRT":
                return "Lehre"
        elif project == "UNICARagil":
            return "Projekt"
        elif project == "DroneMapping":
            return "Forschung"
        elif project == "Mittag" or \
            project == "Pause":
            return "Pause"
        else:
            return "Sonstige"

    def process_time_str(self, s):
        year, month, tmp = s.split("-")
        day, tmp = tmp.split("T")
        hour, minute, tmp = tmp.split(":")
        second, tmp = tmp.split(".")
        microsecond = tmp.split("Z")[0]
        return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(microsecond))

class DataSet:
    def __init__(self, path):
        self.logger = logging.getLogger('data_set')
        self.timers = []
        self.read_csv(path)

    def read_csv(self, path):
        if not os.path.isfile(path):
            raise ValueError("Provided file {} does not exist".format(path))
        if not path[-4:] == ".csv":
            raise ValueError("Received {} but can only process .csv files".format(path))

        with open(path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                self.timers.append(Timer(row["Date"], row["Project"],row["Description"],row["Start Time"],row["End Time"],row["Time (hours)"],row["Notes"]))
                line_count += 1
        self.logger.info("Read csv file from {}.".format(path))

    def teaching_timers(self):
        return [t for t in self.timers if t.main_project =="Lehre"]

    def project_timers(self):
        return [t for t in self.timers if t.main_project =="Projekt"]

    def research_timers(self):
        return [t for t in self.timers if t.main_project =="Forschung"]

    def pause_timers(self):
        return [t for t in self.timers if t.main_project =="Pause"]

    def other_timers(self):
        return [t for t in self.timers if t.main_project =="Sonstige"]

class csvPlotter:
    def __init__(self, csv_file_path, dark_mode = True, font_size = 12):
        self.logger = logging.getLogger('csv_plotter')
        self.data = DataSet(csv_file_path)
        self.define_colors()
        if dark_mode:
            self.bg_color = self.navy
            self.fg_color = self.white
        else:
            self.bg_color = self.white
            self.fg_color = self.navy
        self.font_size = font_size

    def define_colors(self):
        self.blue = self.normalize_color((0, 179, 248))
        self.dark_green = self.normalize_color((30, 130, 76))
        self.green = self.normalize_color((0, 230, 64))
        self.grey = self.normalize_color((46, 49, 49))
        self.light_grey = self.normalize_color((149, 165, 166))
        self.navy = self.normalize_color((34, 40, 54))
        self.orange = self.normalize_color((255, 171, 53))
        self.purple = self.normalize_color((154, 18, 179))
        self.red = self.normalize_color((214, 69, 65))
        self.red_orange = self.normalize_color((211, 84, 0))
        self.white = self.normalize_color((255, 255, 255))
        self.yellow = self.normalize_color((247, 202, 24))

    @staticmethod
    def normalize_color(tup):
        return tuple(float(t)/float(255) for t in tup)

    def pie_chart(self, path):
        # ============
        # Process Data
        # ============
        self.logger.debug("Pie Chart - Computing time shares.")
        total = 0
        for t in self.data.timers:
            total = total + t.duration
        teaching = 0
        for t in self.data.teaching_timers():
            teaching = teaching + t.duration
        project = 0
        for t in self.data.project_timers():
            project = project + t.duration
        research = 0
        for t in self.data.research_timers():
            research = research + t.duration
        # pause = 0
        # for t in self.data.pause_timers():
        #     pause = pause + t.duration
        other = 0
        for t in self.data.other_timers():
            other = other + t.duration

        # ==========
        # Formatting
        # ==========
        self.logger.debug("Pie Chart - Setting plot formatting.")
        title = "Project Shares"
        titleprops = {'fontsize':self.font_size * 1.4, 'color': self.fg_color}
        labels = "Teaching", "Project", "Research", "Other"
        sizes = [teaching, project, research, other]
        colors = [self.blue, self.orange, self.dark_green, self.light_grey]
        startangle = 90
        radius = 3
        explode = (0, 0, 0, 0)
        textprops= {'color':self.fg_color, 'size':self.font_size}
        wedgeprops = {'linewidth': 1, 'linestyle':'-', 'edgecolor':self.fg_color}

        # ================
        # Create Pie Chart
        # ================
        self.logger.debug("Pie Chart - Creating pie chart.")
        fig1, ax1 = plt.subplots()
        fig1.patch.set_facecolor(self.bg_color)
        ax1.set_facecolor(self.bg_color)
        plt.title(title, fontdict = titleprops)
        ax1.pie(sizes, normalize = True, labels=labels, autopct='%1.1f%%',
                startangle=startangle, radius = radius, colors = colors,
                textprops= textprops, wedgeprops = wedgeprops,                
                shadow=False, explode=explode)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # ============
        # Save to File
        # ============
        plt.savefig(path, dpi=300)
        self.logger.info("Pie Chart - Wrote pie chart to {}.".format(path))

def set_logger(name, level=logging.WARN):
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)

    return logger

def parser():
    parser = argparse.ArgumentParser("Draw plots from Time Cop exports.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Path to .csv-file exported from Time Cop.")
    parser.add_argument("-o", "--output", type=str, default="/tmp", help="Output directory where plots will be written to.")
    parser.add_argument("-p", "--pie", action="store_true", help="Whether to generate project share pie chart.")  
    parser.add_argument("-d", "--dark_mode", action="store_true", help="Flip colors to dark mode.")  

    return parser.parse_args()

if __name__ == "__main__":
    data_set_logger = set_logger("data_set", logging.INFO)
    args = parser()

    csv_plotter_logger = set_logger("csv_plotter", logging.INFO)
    csv_plotter = csvPlotter(args.input, dark_mode=args.dark_mode)
    if args.pie:
        csv_plotter.pie_chart(os.path.join(args.output, "pie_chart.png"))