
# -- hoomd simulation
from hoomd_script import *
# generated code for statement <load>
init.read_xml('input.xml')
# generated code for statement <lj_pair>
try:
    lj
except NameError:
    lj = pair.lj(r_cut=2.5)

lj.pair_coeff.set('A', 'A', epsilon=1.0, sigma=1.0)
# generated code for statement <lj_pair>
try:
    lj
except NameError:
    lj = pair.lj(r_cut=2.5)

lj.pair_coeff.set('A', 'B', epsilon=1.0, sigma=1.0)
# generated code for statement <lj_pair>
try:
    lj
except NameError:
    lj = pair.lj(r_cut=2.5)

lj.pair_coeff.set('B', 'B', epsilon=1.0, sigma=1.0)
# generated code for statement <nvt>
integrate.mode_standard(dt=0.005)
integrator = integrate.nvt(group=group.all(), T=1.2, tau=0.5)
# generated code for statement <step>
run(10)
# disable the integrator
integrator.disable()
# -- end simulation