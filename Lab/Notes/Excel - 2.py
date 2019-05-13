import xlsxwriter
import os

filename = "trial.xlsx"
if os.path.isfile(filename):
    os.remove(filename)
workbook = xlsxwriter.Workbook(filename)

sheet1 = workbook.add_worksheet("Sheet 1")

x=1
y=2
z=3

list1=[2.34,4.346,4.234]

sheet1.write(0, 0, "Display")
sheet1.write(1, 0, "Dominance")
sheet1.write(2, 0, "Test")

sheet1.write(0, 1, x)
sheet1.write(1, 1, y)
sheet1.write(2, 1, z)

sheet1.write(4, 0, "Stimulus Time")
sheet1.write(4, 1, "Wacktion Time")

i=4

for n in list1:
    i = i+1
    sheet1.write(i, 0, n)


workbook.close()
