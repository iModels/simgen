simulation_script = """
# -- hoomd simulation
from hoomd_script import *
# generated code for statement <load>
init.read_xml('{{file_name}}')
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
run({{n_step}})
# disable the integrator
integrator.disable()
# -- end simulation"""

# resolve variables in simulation script using locals and globals
from jinja2 import Template, Environment, StrictUndefined
env = Environment(undefined=StrictUndefined, extensions=['jinja2.ext.with_'], trim_blocks=True, cache_size=0)
simulation_script_template = env.from_string(simulation_script)
# this will raise an error if there are variables in the script template (between double curly braces)
# that do not exist in te local or global scope
simulation_script = simulation_script_template.render(dict(globals(), **locals()))

# save simulation script to file
with open('hoomd_sim_script.py', 'w') as f:
    f.write(simulation_script)

from subprocess import call
call(['/usr/local/bin/hoomd', 'hoomd_sim_script.py'])