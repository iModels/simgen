simulation_script = """
# -- simulation
units		lj
dimension	3
atom_style	full

# generated code for statement <load>
read_data {{file_name}}
# generated code for statement <lj_pair>
pair_style	lj/cut 2.5
pair_coeff A A 1.0 1.0 2.5
# generated code for statement <lj_pair>
pair_style	lj/cut 2.5
pair_coeff A B 1.0 1.0 2.5
# generated code for statement <lj_pair>
pair_style	lj/cut 2.5
pair_coeff B B 1.0 1.0 2.5
# generated code for statement <nvt>
fix integrator all nvt temp 1.2 1.2 0.5
# generated code for statement <step>
run {{n_step}}
# disable the integrator
unfix integrator
# -- end simulation"""

# resolve variables in simulation script using locals and globals
from jinja2 import Template, Environment, StrictUndefined
env = Environment(undefined=StrictUndefined, extensions=['jinja2.ext.with_'], trim_blocks=True, cache_size=0)
simulation_script_template = env.from_string(simulation_script)
# this will raise an error if there are variables in the script template (between double curly braces)
# that do not exist in te local or global scope
simulation_script = simulation_script_template.render(dict(globals(), **locals()))

# save simulation script to file
with open('lammps.input', 'w') as f:
    f.write(simulation_script)

from subprocess import call
call(['lammps', '-in', 'lammps.input','-log', 'lammps.log'])