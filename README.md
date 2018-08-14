# operations_geology_tools
GUI application using tkinter and Python to assist in geological drilling operations.

## Features currently implemented

- import surveys from txt or las file.
- calculate surveys directly from MD, INC and AZ input using the minimum curvature method
- interpolate full survey points from either MD or TVD input
- utility to remove duplicate depth values from LAS or TXT curves for import into Wellsight Systems Striplog software
- save well header information in XML file including: Wellname, UWI, Lic number, KB and GRND elevations, UTM E/N wellhead coordinates
  UTM Datum, UTM Zone, Comments, Sampling information
- save surveys in XML file
- export surveys with header information to TXT file

## Features under active development

- import geophysical curves
- plot geophysical curves: define curve scales
- plot surveys in cross section and plan view
- calculate mud lag
- enter formation tops: automatically interpolate TVD from MD or MD from TVD

## Features for future development

- export complete XML file as HTML with CSS stylesheet for print
- implement well planning features
- implement offset wellbore plotting
- implement automated wellpath coding based on reservoir quality

## Dependancies

Python 3.x
matplotlib, tkinter, numpy, xml.etree, bs4
