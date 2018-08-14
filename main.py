from tkinter import *
from tkinter import ttk, messagebox, filedialog, scrolledtext
from geo_modules import import_wellpath, add_survey, interp_depth, calculate_surveys, curve_duplicates
import xml.etree.ElementTree as ET
import os, copy
import matplotlib as mpl
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg
from bs4 import BeautifulSoup


class main_window():

    def __init__(self, master):

        self.master = master
        master.geometry('850x800')
        self.tabControl = ttk.Notebook(self.master)
        self.tab1 = ttk.Frame(self.tabControl)
        self.tab2 = ttk.Frame(self.tabControl)
        self.tab3 = ttk.Frame(self.tabControl)
        self.tab4 = ttk.Frame(self.tabControl)
        self.tab5 = ttk.Frame(self.tabControl)
        self.tab6 = ttk.Frame(self.tabControl)
        self.tab7 = ttk.Frame(self.tabControl)
        self.tab8 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text="Header Info")
        self.tabControl.add(self.tab2, text="Curves")
        self.tabControl.add(self.tab3, text="Surveys")
        self.tabControl.add(self.tab4, text="Formations")
        self.tabControl.add(self.tab5, text="Bit and Mud Records")
        self.tabControl.add(self.tab6, text="Operations")
        self.tabControl.add(self.tab7, text="Sample Descriptions")
        self.tabControl.add(self.tab8, text="Reservoir Evaluation")
        self.tabControl.pack(expand=1, fill='both')

        # menu bar
        menubar = Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Open', command=lambda: main_window.open_wc_params(self))
        filemenu.add_command(label='Save', command=lambda: main_window.save_wc_params(self))
        importmenu = Menu(menubar, tearoff=0)
        importmenu.add_command(label='Import surveys from file', command=lambda: main_window.import_surveys(self))
        importmenu.add_command(label='Import curve data', command=lambda: main_window.import_curve_window(self))
        toolsmenu = Menu(menubar, tearoff=0)
        toolsmenu.add_command(label="Curve Duplicate Fixer", command=lambda: main_window.dup_window(self))
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Import", menu=importmenu)
        menubar.add_cascade(label="Tools", menu=toolsmenu)

        self.master.config(menu=menubar)

        # survey tools GUI

        WCL = Label(self.tab1, text="Well Information", font="bold")
        WCL.grid(row=0, columnspan=4)

        self.wellname_label = Label(self.tab1, text='Wellname')
        self.wellname_label.grid(row=2, column=0, sticky='e')
        self.wellname_entry = Entry(self.tab1)
        self.wellname_entry.insert(END, ' ')
        self.wellname_entry.grid(row=2, column=1, columnspan=3, sticky='ew')

        uwi_label = Label(self.tab1, text="UWI: ")
        uwi_label.grid(row=3, column=0, sticky='e')
        self.uwi_entry = Entry(self.tab1)
        self.uwi_entry.insert(END, ' ')
        self.uwi_entry.grid(row=3, column=1, columnspan=3, sticky='ew')

        grnd_elev_label = Label(self.tab1, text="Grnd Elevation (m):")
        grnd_elev_label.grid(row=4, column=0, sticky='e')
        self.grnd_elev_entry = Entry(self.tab1)
        self.grnd_elev_entry.insert(END, '0.0')
        self.grnd_elev_entry.grid(row=4, column=1)

        self.kb_elev_label = Label(self.tab1, text="KB Elevation (m):")
        self.kb_elev_label.grid(row=4, column=2, sticky='e')
        self.kb_elev_entry = Entry(self.tab1)
        self.kb_elev_entry.insert(END, '0.0')
        self.kb_elev_entry.grid(row=4, column=3)

        utm_e_label = Label(self.tab1, text="UTM Easting:")
        utm_e_label.grid(row=5, column=0, sticky='e')
        self.utm_e_entry = Entry(self.tab1)
        self.utm_e_entry.insert(END, '0.0')
        self.utm_e_entry.grid(row=5, column=1)

        utm_n_label = Label(self.tab1, text="UTM Northing:")
        utm_n_label.grid(row=5, column=2, sticky='e')
        self.utm_n_entry = Entry(self.tab1)
        self.utm_n_entry.insert(END, '0.0')
        self.utm_n_entry.grid(row=5, column=3)

        utm_datum_label = Label(self.tab1, text="UTM Datum:")
        utm_datum_label.grid(row=6, column=0, sticky='e')
        self.utm_datum_entry = Entry(self.tab1)
        self.utm_datum_entry.insert(END, 'NAD 83/NAD 27')
        self.utm_datum_entry.grid(row=6, column=1)

        utm_zone_label = Label(self.tab1, text="UTM Zone:")
        utm_zone_label.grid(row=6, column=2, sticky='e')
        self.utm_zone_entry = Entry(self.tab1)
        self.utm_zone_entry.insert(END, '12N')
        self.utm_zone_entry.grid(row=6, column=3)

        afe_label = Label(self.tab1, text='AFE:')
        afe_label.grid(row=7, column=0, sticky='e')
        self.afe_entry = Entry(self.tab1)
        self.afe_entry.insert(END, ' ')
        self.afe_entry.grid(row=7, column=1)

        lic_num_label = Label(self.tab1, text='License #')
        lic_num_label.grid(row=7, column=2, sticky='e')
        self.lic_num_entry = Entry(self.tab1)
        self.lic_num_entry.insert(END, ' ')
        self.lic_num_entry.grid(row=7, column=3)

        field_label = Label(self.tab1, text='Field:')
        field_label.grid(row=8, column=0, sticky='e')
        self.field_entry = Entry(self.tab1)
        self.field_entry.insert(END, '0.0')
        self.field_entry.grid(row=8, column=1)

        objective_label = Label(self.tab1, text='Objective:')
        objective_label.grid(row=8, column=2, sticky='e')
        self.objective_entry = Entry(self.tab1)
        self.objective_entry.insert(END, ' ')
        self.objective_entry.grid(row=8, column=3)

        spud_date_label = Label(self.tab1, text='Spud Date:')
        spud_date_label.grid(row=9, column=0, sticky='e')
        self.spud_date_entry = Entry(self.tab1)
        self.spud_date_entry.insert(END, 'dd/mm/yyyy XX:XX hrs')
        self.spud_date_entry.grid(row=9, column=1)

        td_depth_label = Label(self.tab1, text='FTD Depth (m):')
        td_depth_label.grid(row=9, column=2, sticky='e')
        self.td_depth_entry = Entry(self.tab1)
        self.td_depth_entry.insert(END, '0.0')
        self.td_depth_entry.grid(row=9, column=3)

        td_date_label = Label(self.tab1, text='TD Date:')
        td_date_label.grid(row=10, column=0, sticky='e')
        self.td_date_entry = Entry(self.tab1)
        self.td_date_entry.insert(END, 'dd/mm/yyyy XX:XX hrs')
        self.td_date_entry.grid(row=10, column=1)

        operator_label = Label(self.tab1, text='Operating Company:')
        operator_label.grid(row=11, column=0, columnspan=1, sticky='e')
        self.operator_entry = Entry(self.tab1)
        self.operator_entry.insert(END, ' ')
        self.operator_entry.grid(row=11, column=1, columnspan=3, sticky='ew')

        contractor_label = Label(self.tab1, text='Drilling Contractor:')
        contractor_label.grid(row=12, column=0, columnspan=1, sticky='e')
        self.contractor_entry = Entry(self.tab1)
        self.contractor_entry.insert(END, ' ')
        self.contractor_entry.grid(row=12, column=1, columnspan=3, sticky='ew')

        sampling_label = Label(self.tab1, text='Samples:')
        sampling_label.grid(row=13, column=0, sticky='e')
        self.sampling_entry = scrolledtext.ScrolledText(self.tab1, height='3', width='40')
        self.sampling_entry.insert(END, ' ')
        self.sampling_entry.grid(row=13, column=1, columnspan=3, sticky='w')

        comments_label = Label(self.tab1, text='Comments:')
        comments_label.grid(row=14, column=0, sticky='e')
        self.comments_entry = scrolledtext.ScrolledText(self.tab1, height='5', width='40')
        self.comments_entry.insert(END, ' ')
        self.comments_entry.grid(row=14, column=1, columnspan=3, sticky='w')

        # Curves Tab
        rf_curve_btn = Button(self.tab2, text="Refresh Curves", command=lambda: self.refresh_curves())
        rf_curve_btn.grid(row=0, column=0)
        self.curve_box = scrolledtext.ScrolledText(self.tab2, width=80, height=20)
        self.curve_box.grid(row=1, column=0)

        # Survey Tab

        b1 = Button(self.tab3, text="Export surveys", command=lambda: self.show_surveys())
        b1.grid(row=0, column=0)

        b2 = Button(self.tab3, text="Calculate and refresh Surveys", command=lambda: self.refresh_surveys())
        b2.grid(row=0, column=2)

        self.survey_box = scrolledtext.ScrolledText(self.tab3, height='20', width='90')
        self.survey_box.grid(row=1, column=0, columnspan=15)

        insert_surv_title = Label(self.tab3, text='Insert New Survey')
        insert_surv_title.grid(row=2, column=0, columnspan=15)

        md_label = Label(self.tab3, text="MD")
        inc_label = Label(self.tab3, text="INC")
        az_label = Label(self.tab3, text="AZ")
        md_label.grid(row=3, column=0)
        inc_label.grid(row=3, column=1)
        az_label.grid(row=3, column=2)

        md_entry = Entry(self.tab3)
        inc_entry = Entry(self.tab3)
        az_entry = Entry(self.tab3)
        md_entry.grid(row=4, column=0)
        inc_entry.grid(row=4, column=1)
        az_entry.grid(row=4, column=2)

        add_surv_btn = Button(self.tab3, text='Add Survey',
                              command=lambda: self.add_new_survey(md_entry, inc_entry, az_entry))
        add_surv_btn.grid(row=4, column=3)

        delete_surv_title = Label(self.tab3, text='Delete Survey at depth (MD)')
        delete_surv_title.grid(row=5, column=0, columnspan=15)

        delete_label = Label(self.tab3, text="MD")
        delete_label.grid(row=6, column=0)
        delete_entry = Entry(self.tab3)
        delete_entry.grid(row=7, column=0)
        delete_surv_btn = Button(self.tab3, text="Delete",
                                 command=lambda: self.delete_survey(float(delete_entry.get())))
        delete_surv_btn.grid(row=7, column=3)

        interp_surv_title = Label(self.tab3, text='Interpolate Survey')
        interp_surv_title.grid(row=8, column=0, columnspan=15)

        self.interp_depth_label = Label(self.tab3, text="Depth")
        self.interp_depth_label.grid(row=10, column=0)
        self.interp_depth_entry = Entry(self.tab3)
        self.interp_depth_entry.grid(row=10, column=1)
        self.interp_depth_entry.insert(END, '0.0')
        self.box_val = StringVar()
        self.interp_surv_type = ttk.Combobox(self.tab3, textvariable=self.box_val)
        self.interp_surv_type["values"] = ('MD', 'TVD')
        self.interp_surv_type.current(0)
        self.interp_surv_type.grid(row=10, column=2)
        self.interp_surv_btn = Button(self.tab3, text="Interpolate",
                                 command=lambda: self.interp_survey(self.interp_surv_type.get(), float(self.interp_depth_entry.get())))
        self.interp_surv_btn.grid(row=10, column=3)

    def import_surveys(self):
        # Open window to ask which columns are MD, INC and AZ
        self.newWindow = Toplevel(self.master)
        self.newWindow.wm_title('Import Surveys')
        self.newWindow.geometry('400x200')
        localMaster = self.newWindow

        survey_file = filedialog.askopenfilename(title="Select survey file", filetypes=(
            ("text files", "*.txt"), ("LAS files", "*.las"), ("all files", "*.*")))

        md_col_label = Label(localMaster, text='Enter the MD column number:')
        md_col_label.grid(row=0, column=0, sticky='e')
        md_col_entry = Entry(localMaster)
        md_col_entry.grid(row=0, column=1)

        inc_col_label = Label(localMaster, text='Enter the INC column number:')
        inc_col_label.grid(row=1, column=0, sticky='e')
        inc_col_entry = Entry(localMaster)
        inc_col_entry.grid(row=1, column=1)

        az_col_label = Label(localMaster, text='Enter the AZ column number:')
        az_col_label.grid(row=2, column=0, sticky='e')
        az_col_entry = Entry(localMaster)
        az_col_entry.grid(row=2, column=1)

        import_btn = Button(localMaster, text="Import",
                            command=lambda: main_window.import_wellpath(self, [int(md_col_entry.get()) - 1,
                                                                               int(inc_col_entry.get()) - 1,
                                                                               int(az_col_entry.get()) - 1],
                                                                        survey_file))
        import_btn.grid(row=3, column=1)

    def import_wellpath(self, col_nums, survey_file):
        # import a wellpath from a survey file, column numbers for (MD, INC, AZM)
        # look for rows containing survey data, ignore blank lines
        WellInfo.survey_list = []
        with open(survey_file, 'r') as sf:
            for line in sf:
                # strip newlines and spaces off either end of the line then split based on column
                line = line.strip().split()
                # check to see if line starts with a number, otherwise ignore
                if len(line) and line[0][0].isdigit():
                    md, inc, azm = float(line[col_nums[0]]), float(line[col_nums[1]]), float(line[col_nums[2]])
                    WellInfo.survey_list.append((md, inc, azm))
                else:
                    pass

        messagebox.showinfo('Import Success', 'Wellpath imported successfully')
        self.newWindow.destroy()
        self.refresh_surveys()

    def show_surveys(self):

        WellInfo.calced_surveys = calculate_surveys(WellInfo.survey_list, WellInfo.kb_elev)
        with open('Surveys', 'w') as tempfile:
            # set up spacing for 10 characters
            s8, s7 = ' ' * 8, ' ' * 7
            tempfile.write('# Well Center Information #\n')
            tempfile.write('{}\n'.format(str(WellInfo.wellname)))
            tempfile.write('{}\n'.format(str(WellInfo.uwi)))
            print(WellInfo.uwi)
            tempfile.write('GRND Elevation: {}m\n'.format(str(WellInfo.grnd_elev)))
            tempfile.write('KB Elevation: {}m\n'.format(str(WellInfo.kb_elev)))
            tempfile.write('UTM Northing: {}, UTM Easting: {}\n'.format(WellInfo.utm_N, WellInfo.utm_E))
            tempfile.write('#' * 90 + '\n')
            tempfile.write('MD{}INC{}AZ{}TVD{}N {}E {}VS{}DLS{}SS \n'.format(s8, s7, s8, s7, s8, s8, s8, s7))
            WellInfo.final_surveys = [
                ('MD{}INC{}AZ{}TVD{}N {}E {}VS{}DLS{}SS \n'.format(s8, s7, s8, s7, s8, s8, s8, s7))]
            for line in WellInfo.calced_surveys:
                new_line = []
                for item in line:
                    # adding spaces to make output pretty
                    if len(str(item)) != 10:
                        add_spaces = 10 - len(str(item))
                        item = str(item) + ' ' * add_spaces
                        new_line.append(item)
                    else:
                        new_line.append(str(item))
                tempfile.write(''.join(new_line) + '\n')
                WellInfo.final_surveys.append(new_line)
        self.show_survey_window()

    def refresh_surveys(self):
        if WellInfo.kb_elev == 0.0:
            try:
                kb_float = float(self.kb_elev_entry.get())
            except:
                kb_float = 0.0
        WellInfo.calced_surveys = calculate_surveys(WellInfo.survey_list, kb_float)
        # clear existing surveys
        self.survey_box.config(state=NORMAL)
        self.survey_box.delete('1.0', END)

        s8, s7 = ' ' * 8, ' ' * 7
        self.survey_box.insert('end',
                               ('MD{}INC{}AZ{}TVD{}N {}E {}VS{}DLS{}SS \n'.format(s8, s7, s8, s7, s8, s8, s8, s7)))
        WellInfo.final_surveys = [
            ('MD{}INC{}AZ{}TVD{}N {}E {}VS{}DLS{}SS \n'.format(s8, s7, s8, s7, s8, s8, s8, s7))]
        for line in WellInfo.calced_surveys:
            new_line = []
            for item in line:
                # adding spaces to make output pretty
                if len(str(item)) != 10:
                    add_spaces = 10 - len(str(item))
                    item = str(item) + ' ' * add_spaces
                    new_line.append(item)
                    self.survey_box.insert('end', item)
                else:
                    new_line.append(str(item))
                    self.survey_box.insert('end', str(item))
            WellInfo.final_surveys.append(new_line)
        # make the box read only
        self.survey_box.config(state=DISABLED)

    def refresh_curves(self):
        pass

    def add_new_survey(self, md_col, inc_col, az_col):

        md, inc, az = float(md_col.get()), float(inc_col.get()), float(az_col.get())
        WellInfo.survey_list.append((md, inc, az))
        WellInfo.survey_list.sort(key=lambda tup: tup[0])
        self.refresh_surveys()

    def interp_survey(self, survey_type, depth):
        kb = float(self.kb_elev_entry.get()) # pull from the entry box so that it doesn't need to be saved
        interp_survey = interp_depth(WellInfo.calced_surveys, survey_type, depth, kb)
        self.newWindow = Toplevel(self.master)
        self.newWindow.wm_title('Interpolated Survey')
        self.newWindow.geometry('550x50')
        localMaster = self.newWindow

        text_line = ""

        spaces = []
        for item in interp_survey:
            spaces.append(len(str(item)) - 2)
            text_line = text_line + str(item)+' '

        sp1, sp2, sp3, sp4, sp5, sp6, sp7, sp8 = spaces[0] * ' ', spaces[1] * ' ', spaces[2] * ' ', spaces[3] * ' ', \
                                                 spaces[4] * ' ', spaces[5] * ' ', spaces[6] * ' ', spaces[7] * ' '

        text_lines = 'MD {}INC{}AZ {}TVD{}NS {}EW {}VS {}DLS{}SS\n'.format(sp1, sp2, sp3, sp4, sp5, sp6, sp7,
                                                                           sp8) + text_line
        svy_text = Text(localMaster, height=2, width=90)
        svy_text.pack()
        svy_text.config(state=NORMAL)
        svy_text.insert(END, text_lines)
        svy_text.config(state=DISABLED)
        # messagebox.showinfo(title='bleh', message=str(interp_survey))

    def delete_survey(self, depth):
        # get index of survey and delete it
        idx = [y[0] for y in WellInfo.survey_list].index(depth)
        del WellInfo.survey_list[idx]
        self.refresh_surveys()

    def show_survey_window(self):
        self.newWindow = Toplevel(self.master)
        bb = SurveyWindow(self.newWindow)
        self.frame = Frame(self.master)

    def import_curve_window(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.wm_title('Import Curve')
        self.newWindow.geometry('400x200')
        localMaster = self.newWindow

        curve_file = filedialog.askopenfilename(title="Select curve file", filetypes=(
            ("text files", "*.txt"), ("LAS files", "*.las"), ("all files", "*.*")))

        curve_name_label = Label(localMaster, text='Enter the Curve Name:')
        curve_name_label.grid(row=0, column=0, sticky='e')
        curve_name_entry = Entry(localMaster)
        curve_name_entry.grid(row=0, column=1)

        depth_col_label = Label(localMaster, text='Enter the depth column number:')
        depth_col_label.grid(row=1, column=0, sticky='e')
        depth_col_entry = Entry(localMaster)
        depth_col_entry.grid(row=1, column=1)

        value_col_label = Label(localMaster, text='Enter the curve value column number:')
        value_col_label.grid(row=2, column=0, sticky='e')
        value_col_entry = Entry(localMaster)
        value_col_entry.grid(row=2, column=1)

        import_btn = Button(localMaster, text="Import",
                            command=lambda: main_window.import_curve(self, [curve_name_entry.get(),
                                                                            int(depth_col_entry.get()) - 1,
                                                                            int(value_col_entry.get()) - 1],
                                                                     curve_file))
        import_btn.grid(row=3, column=1)

    def import_curve(self, params, curve_file):
        with open(curve_file, 'r') as self.sf:
            self.curve_lines = []
            self.curve_name = params[0]
            for line in self.sf:
                # strip newlines and spaces off either end of the line then split based on column
                line = line.strip().split()
                # check to see if line starts with a number, otherwise ignore
                if len(line) and line[0][0].isdigit():
                    depth, value = float(line[params[1]]), float(line[params[2]])
                    self.curve_lines.append((depth, value))
                else:
                    pass
        try:
            del WellInfo.curve_points[self.curve_name]
        except:
            pass
        WellInfo.curve_points[self.curve_name] = self.curve_lines
        messagebox.showinfo('Import Success', 'Curve imported successfully')
        self.newWindow.destroy()
        self.refresh_curves()

    def dup_window(self):
        # define and call the duplicate curve utility
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry('350x200')
        self.newWindow.title('Remove Duplicate Depths')
        self.dupFrame = Frame(self.newWindow)
        self.dupFrame.pack(fill=BOTH, expand=TRUE)

        self.frame1 = Frame(self.dupFrame)
        self.frame1.pack(fill=X)

        self.L1 = Label(self.frame1, text="Enter curve number with duplicate values")
        self.L1.pack(side=TOP)
        self.E1 = Entry(self.frame1)
        self.E1.pack(side=BOTTOM)

        self.frame2 = Frame(self.dupFrame)
        self.frame2.pack(fill=X)

        b = Button(self.frame2, text="Select File", command=lambda: curve_duplicates(int(self.E1.get())))
        b.pack()

    def save_wc_params(self):

        WellInfo.filename = filedialog.asksaveasfilename()
        # make sure extension is *.wlf
        '''
        if WellInfo.filename[-4:] == '.wlf':
            pass
        elif '.' not in WellInfo.filename:
            WellInfo.filename = WellInfo.filename + '.wlf'
        else:
            WellInfo.filename = WellInfo.filename[:-4] + '.wlf'
        '''

        well_root = ET.Element('WELL')
        well_header = ET.SubElement(well_root, 'HEADER')
        well_surveys = ET.SubElement(well_root, 'SURVEYS')

        WellInfo.wellname = self.wellname_entry.get()
        ET.SubElement(well_header, 'Wellname').text = WellInfo.wellname
        WellInfo.uwi = self.uwi_entry.get()
        ET.SubElement(well_header, 'UWI').text = WellInfo.uwi
        WellInfo.grnd_elev = self.grnd_elev_entry.get()
        ET.SubElement(well_header, 'GRND').text = WellInfo.grnd_elev
        WellInfo.kb_elev = self.kb_elev_entry.get()
        ET.SubElement(well_header, 'KB').text = WellInfo.kb_elev
        WellInfo.utm_E = self.utm_e_entry.get()
        ET.SubElement(well_header, 'UTME').text = WellInfo.utm_E
        WellInfo.utm_N = self.utm_n_entry.get()
        ET.SubElement(well_header, 'UTMN').text = WellInfo.utm_N
        WellInfo.utm_datum = self.utm_datum_entry.get()
        ET.SubElement(well_header, 'UTMD').text = WellInfo.utm_datum
        WellInfo.utm_zone = self.utm_zone_entry.get()
        ET.SubElement(well_header, 'UTMZ').text = WellInfo.utm_zone
        WellInfo.afe = self.afe_entry.get()
        ET.SubElement(well_header, 'AFE').text = WellInfo.afe
        WellInfo.license_number = self.lic_num_entry.get()
        ET.SubElement(well_header, 'LIC').text = WellInfo.license_number
        WellInfo.field = self.field_entry.get()
        ET.SubElement(well_header, 'FIELD').text = WellInfo.field
        WellInfo.contractor = self.contractor_entry.get()
        ET.SubElement(well_header, 'CONTRACTOR').text = WellInfo.contractor
        WellInfo.operator = self.operator_entry.get()
        ET.SubElement(well_header, 'OPERATOR').text = WellInfo.operator
        WellInfo.spud_date = self.spud_date_entry.get()
        ET.SubElement(well_header, 'SPUDDATE').text = WellInfo.spud_date
        WellInfo.td_date = self.td_date_entry.get()
        ET.SubElement(well_header, 'TDDATE').text = WellInfo.td_date
        WellInfo.td_depth = self.td_depth_entry.get()
        ET.SubElement(well_header, 'TDDEPTH').text = WellInfo.td_depth
        WellInfo.objective = self.objective_entry.get()
        ET.SubElement(well_header, 'OBJECTIVE').text = WellInfo.objective
        WellInfo.sampling = self.sampling_entry.get('0.0', END)
        ET.SubElement(well_header, 'SAMPLING').text = WellInfo.sampling
        WellInfo.comments = self.comments_entry.get('0.0', END)
        ET.SubElement(well_header, 'COMMENTS').text = WellInfo.comments

        svy_count = 0
        for survey in WellInfo.final_surveys[1:]:
            survey_line = []
            for item in survey:
                survey_line.append(item)
            ET.SubElement(well_surveys, 'SV').text = str(survey_line)[1:-1]
            svy_count += 1

        tree = ET.ElementTree(well_root)
        tree.write(WellInfo.filename)

    def open_wc_params(self):
        try:
            WellInfo.filename = filedialog.askopenfilename()
            # make sure extension is *.wlf
            well = ET.parse(WellInfo.filename)
            well_root = well.getroot()

            info_dict = {}

            for survey in well_root.iter('SV'):
                survey_line = []
                items = survey.text.split(',')
                for item in items:
                    survey_line.append(item.strip()[1:-1].rstrip())
                md, inc, az = survey_line[0], survey_line[1], survey_line[2]
                WellInfo.survey_list.append((float(md), float(inc), float(az)))

            self.refresh_surveys()

        except:
            messagebox.showerror('Failed', 'Please check to make sure this is a well file')


class WellInfo():
    # this class holds all the information to populate the report fields
    filename = ''
    wellname = None
    uwi = None
    objective = ''
    license_number = ''
    afe = ''
    field = ''
    kb_elev = 0.0
    grnd_elev = 0.0
    operator = ''
    contractor = ''
    geologists = []
    directional_company = ''
    spud_date = ''
    td_date = ''
    td_depth = ''
    hole_size = {}  # dictionary format is surface: size
    casing_info = {}  # dictionary same as hole size
    sampling = ''  # string to let geologist indicate sampling interval
    comments = ''  # string for generic comments, separated by comma
    summary = ''  # string for summary
    formations = []  # list of formations
    utm_N = 0
    utm_E = 0
    utm_datum = None
    utm_zone = None
    survey_list = []
    calced_surveys = []
    final_surveys = []
    curve_points = {}  # {key: [{depth, value, tvd)]}


class SurveyWindow():
    def __init__(self, master):
        from tkinter import filedialog

        def save_surveys():
            from shutil import copyfile
            save_name = filedialog.asksaveasfilename(title="Save As...", filetypes=(
                ("text files", "*.txt"), ("all files", "*.*")))
            if save_name[:-3] != 'txt':
                save_name = save_name + '.txt'
            copyfile('Surveys', save_name)
            os.remove('Surveys')

        self.master = master
        self.master.title('Surveys')
        self.master = Frame(master)
        self.master.pack(side='top')

        curve_file = 'Surveys'

        text = scrolledtext.ScrolledText(self.master, width=90, height=30)
        text.pack()
        text.config(state=NORMAL)

        text.insert('1.0', open(curve_file, 'r').read())
        text.config(state=DISABLED)
        Button(self.master, text='Save Surveys As...', command=save_surveys).pack(pady=15)


if __name__ == '__main__':
    root = Tk()
    b = main_window(root)
    root.title("Wellsite Tools")
    root.mainloop()
