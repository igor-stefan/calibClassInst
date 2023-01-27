from calib import *

#tbc stands for to be calibrated
#here we are initializing three instances of class Measurement
#first argument is the value measured, second argument is the resolution
tbc0 = Measurement(.46, 1e-2)
tbc1 = Measurement(2.54, 1e-2)
tbc2 = Measurement(4.62, 1e-2)

#std stands fot standard
#same as above
std0 = Measurement(.5, 1e-2)
std1 = Measurement(2.5, 1e-2)
std2 = Measurement(4.67, 1e-2)

#after creating the set of measurements
#instantiate the standard equipment 
#pass the name, the pct of uncertainty and the digits (prolly can be found in the manual of equipment)
#then pass all the measures correspondent to this equipment (in this case all with prefix std)
comercial = Standard("vonder", 2.5, 5, std0, std1, std2)

# instantiate the equipment to be calibrated
#pass the name and all the measures correspondent to it
developed = Equipment("custom", tbc0, tbc1, tbc2)

#instantiante the class Calibration in variable process
process = Calibration(comercial, developed, 10)

#get results
process.values()

#get graphic results
#pass a valid index from array results 
process.graph(2, to_save=False)