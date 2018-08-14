import os, math
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt

'''This file is the original work of Tyler Pubben of Silver Spring Energy Consulting Ltd. Any commercial use is
strictly prohibited without prior written consent. Visit www.silverspringenergy.com to contact the author'''


def curve_duplicates(curve_entry):
    col_v = int(curve_entry)
    duplicate_curve = col_v - 1
    curve_file = filedialog.askopenfilename(title="Select curve file", filetypes=(
        ("text files", "*.txt"), ("LAS files", "*.las"), ("all files", "*.*")))
    # open and read curve file lines to list

    with open(curve_file, 'r') as curves:
        # use a set to take first values for each based on the duplicate column
        seen = set()
        uniq = []
        for depth in curves:
            line = depth.strip().split()
            if len(line) > 0 and not line[0][0].isdigit():
                uniq.append(depth)
            elif len(line) > 0 and line[0][0].isdigit():
                depth_filter = float(line[duplicate_curve])
                if depth_filter not in seen:
                    uniq.append(depth)
                    seen.add(depth_filter)
                else:
                    pass
            else:
                pass

    os.remove(curve_file)
    with open(curve_file, 'a') as curves:
        for line in uniq:
            curves.write(line)
    messagebox.showinfo("Status", "Curve Successfully Processed")


def import_wellpath(col_nums, survey_file):
    import main
    print(col_nums)
    # import a wellpath from a survey file, column numbers for (MD, INC, AZM)
    # look for rows containing survey data, ignore blank lines
    main.WellInfo.survey_list = []
    with open(survey_file, 'r') as sf:
        for line in sf:
            # strip newlines and spaces off either end of the line then split based on column
            line = line.strip().split()
            # check to see if line starts with a number, otherwise ignore
            if line[0][0].isdigit():
                md, inc, azm = line[col_nums[0]], line[col_nums[1]], line[col_nums[2]]
                main.WellInfo.survey_list.append((md, inc, azm))
            else:
                pass

    result = (survey_file, main.WellInfo.survey_list)
    messagebox.showinfo('Import Success', 'Wellpath imported successfully')
    return result


def calculate_surveys(surveys, kb_elev):
    from math import radians as rad
    from math import degrees as deg
    kb_elev = float(kb_elev)
    # surveys parameter is list of surveys in tuple (md, inc, az, ...) where only the first 3 are needed.
    # minimum curvature method, requires two survey points
    counter, count = len(surveys), 0
    # initialize output surveys with first survey point as it by default has a northing/easting value of 0,0
    # tuple in output surveys is (md, inc, azm, tvd, north, east, vs, dls, ss)
    output_surveys = [(0, 0, 0, 0, 0, 0, 0, 0, kb_elev)]
    tvd, east, north = 0, 0, 0
    while count < counter - 1:
        # formulas found on http://www.drillingformulas.com/minimum-curvature-method/
        ptA, ptB = surveys[count], surveys[count + 1]
        mdA, mdB = float(ptA[0]), float(ptB[0])
        md_diff = mdB - mdA
        ptA_inc, ptB_inc, ptA_az, ptB_az = rad(float(ptA[1])), rad(float(ptB[1])), rad(float(ptA[2])), rad(
            float(ptB[2]))
        b = math.acos(
            math.cos(ptB_inc - ptA_inc) - (math.sin(ptA_inc) * math.sin(ptB_inc) * (1 - math.cos(ptB_az - ptA_az))))
        if b == 0:
            rf = 1.0
        else:
            rf = (2.0 / b) * math.tan(b / 2.0)
        north_diff = (md_diff / 2) * (math.sin(ptA_inc) * math.cos(ptA_az) + math.sin(ptB_inc) * math.cos(ptB_az)) * rf
        north = north + north_diff
        east_diff = (md_diff / 2) * (math.sin(ptA_inc) * math.sin(ptA_az) + math.sin(ptB_inc) * math.sin(ptB_az)) * rf
        east = east + east_diff
        tvd_diff = (md_diff / 2) * (math.cos(ptA_inc) + math.cos(ptB_inc)) * rf
        tvd = tvd + tvd_diff
        # hd is the horizontal displacement between points A and B
        vs = math.sqrt((north * north) + (east * east))
        dls = abs(((deg(ptB_inc) - deg(ptA_inc)) / md_diff) * 30.0)
        tvdss = kb_elev - tvd
        output_surveys.append((mdB, deg(ptB_inc), deg(ptB_az), tvd, north, east, vs, dls, tvdss))
        count += 1
    final_surveys = []
    for item in output_surveys:
        line = (
            round(item[0], 2), round(item[1], 2), round(item[2], 2), round(item[3], 2), round(item[4], 2),
            round(item[5], 2), round(item[6], 2), round(item[7], 2), round(item[8], 2))
        final_surveys.append(line)

    return final_surveys


def add_survey(surveys, new_survey):
    """
    Add survey to list of surveys then reorder list base on MD, survey list is list of tuples (md, inc, azm, *).
    surveys parameter is existing list. new_surveys parameter is survey to be added. new_surveys should
    be tuple of (md, inc, az). Brute force method for now just recalculates all the surveys since computation
    time is negligible.
    """
    # inject new survey into survey list, then sorting new surveys into list based on MD depth
    surveys.append(new_survey)
    surveys.sort(key=lambda tup: tup[0])  # sorts list in place

    return surveys


def interp_depth(surveys, survey_type, depth, kb_elev):
    """ surv_type is either MD or TVD. If user is looking to interp based off of TVD, type == TVD.
    Depth parameter is the TVD or MD to interpolate. Surveys parameter is the input survey list"""

    while True: # set in a while true loop to allow for it to be run repeatedly without stacking interps
        in_surveys = surveys.copy()
        survey_list = []
        for item in in_surveys:
            md, inc, az = item[0], item[1], item[2]
            survey_list.append((md, inc, az))
        # find where survey fits in list, then find out surveys above and below and calculate interp survey md, inc, az
        if survey_type == 'MD': # looking for TVD
            idx = min(range(len(in_surveys)), key=lambda i: abs(float(in_surveys[i][0])-depth))
            if float(in_surveys[idx][0]) > depth:
                idx = idx - 1
            previous_survey, next_survey = in_surveys[idx], in_surveys[idx+1]
            ratio = (depth - float(previous_survey[0]))/(float(next_survey[0]) - float(previous_survey[0]))
            interp_inc = (float(next_survey[1]) - float(previous_survey[1])) * ratio + float(previous_survey[1])
            next_az, prev_az = float(next_survey[2]), float(previous_survey[2])
            # define quadrants
            q1, q2, q3, q4 = (0, 90), (90, 180), (180, 270), (270, 360)
            if q1[0] <= next_az < q1[1] and q4[0] <= prev_az < q4 [1]:
                prev_az = 0 - (360 - prev_az) # sets the previous az to behind 0
                az_diff = next_az - prev_az
                interp_az = az_diff * ratio + prev_az
                if interp_az < 0:
                    interp_az = 360 - abs(interp_az)
            elif q4[0] <= next_az < q4[1] and q1[0] <= prev_az < q1[1]:
                prev_az = 360 + prev_az # make prev az greater than 360
                az_diff = abs(prev_az - next_az)
                interp_az = prev_az - (az_diff * ratio)
                if interp_az > 360:
                    interp_az = interp_az - 360
            else:
                az_diff = next_az - prev_az
                interp_az = az_diff * ratio + prev_az

            survey_list.append((depth, interp_inc, interp_az))
            survey_list.sort(key=lambda tup: tup[0])

        else:
            idx = min(range(len(in_surveys)), key=lambda i: abs(float(in_surveys[i][3]) - depth))
            if float(in_surveys[idx][3]) > depth:
                idx = idx - 1
            previous_survey, next_survey = in_surveys[idx], in_surveys[idx + 1]
            ratio = (depth - float(previous_survey[3])) / (float(next_survey[3]) - float(previous_survey[3]))
            interp_md = (float(next_survey[0] - float(previous_survey[0]))) * ratio + float(previous_survey[0])
            interp_inc = (float(next_survey[1]) - float(previous_survey[1])) * ratio + float(previous_survey[1])
            next_az, prev_az = float(next_survey[2]), float(previous_survey[2])
            # define quadrants
            q1, q2, q3, q4 = (0, 90), (90, 180), (180, 270), (270, 360)
            if q1[0] <= next_az < q1[1] and q4[0] <= prev_az < q4[1]:
                prev_az = 0 - (360 - prev_az)  # sets the previous az to behind 0
                az_diff = next_az - prev_az
                interp_az = az_diff * ratio + prev_az
                if interp_az < 0:
                    interp_az = 360 - abs(interp_az)
            elif q4[0] <= next_az < q4[1] and q1[0] <= prev_az < q1[1]:
                prev_az = 360 + prev_az  # make prev az greater than 360
                az_diff = abs(prev_az - next_az)
                interp_az = prev_az - (az_diff * ratio)
                if interp_az > 360:
                    interp_az = interp_az - 360
            else:
                az_diff = next_az - prev_az
                interp_az = az_diff * ratio + prev_az

            survey_list.append((interp_md, interp_inc, interp_az))
            survey_list.sort(key=lambda tup: tup[0])

        interp_svy = calculate_surveys(survey_list, kb_elev)[idx+1]
        return interp_svy
        break


def lag_calculation(pump_rate, hole_diam, pipe_diam, hole_wash, units):
    """ This function calculates appropriate gas/sample lag based on hole diameter, pump rate and pipe OD"""
    if units == 'Metric':
        r2 = (((float(hole_diam) / 100) * (1 + float(hole_wash) / 100)) / 2) ** 2
        h = 100
        hole_vol = math.pi * r2 * h
        min_100m = hole_vol / pump_rate
        ann_vel = 1 / (min_100m / 100)

        messagebox.showinfo('Lag parameters', '{}m/min\n{}min/100m'.format(str(ann_vel), str(min_100m)))
    pass


def plot_wellpath(surveys, plot_range):
    """ This function plots wellpath in both planar and cross section view. Options for showing data curves and
    the MD range of the wellpath to be plotted. plot_range is tuple of values"""
    x1_points, x2_points, y1_points, y2_points = [], [], [], []
    for survey in surveys:
        x_point, z_point = float(survey[0]), float(survey[-1])  # index 0 is MD, index -1 is SS
        x1_points.append(float(survey[5]))
        y1_points.append(float(survey[4]))  # take eastings and northings for map view
        if plot_range[0] <= x_point <= plot_range[1]:
            x2_points.append(x_point)
            y2_points.append(z_point)

    fig, (ax1, ax2) = plt.subplots(2)
    ax1.plot(x1_points, y1_points, 'k ')
    ax1.set(title='Plan view', xlabel='Easting UTM (m)', ylabel='Northing UTM (m)')

    ax2.plot(x2_points, y2_points, 'k ')
    ax2.set(title='Cross section view', xlabel='Measured Depth (m)', ylabel='SubSea Depth (m)')

    plt.show()


def import_curves():
    """ This function imports curve data into appropriate columns. Use dictionary to name columns"""
    curve_file = filedialog.askopenfilename(title="Select curve file", filetypes=(
        ("text files", "*.txt"), ("LAS files", "*.las"), ("all files", "*.*")))
    # open and read curve file lines to list

    # with open(curve_file, 'r') as curves:

    pass


def import_descriptions():
    """ This function imports geologic descriptions from txt file for use in report generation """
    pass


def create_well():
    """ Creates a new well and well file associated with the report. """
    pass


def save_well():
    """ Saves current changes to well """
    pass


def open_well():
    """ opens a well to edit or view """
    pass
