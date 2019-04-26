import axographio
import matplotlib.pyplot as plt
import numpy as np

inputfile = axographio.read("012519 059_csd.axgr")

plt.figure()
for x in range(14):
    plt.plot(inputfile.data[x+1])
plt.xlabel(inputfile.names[0])
plt.ylabel(inputfile.names[1]);
plt.show()
