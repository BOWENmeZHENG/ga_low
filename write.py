def write_files(num_total_real, coors_flakes_all, coors_inclusions, L_box, seed,
                sigma, num_cycle, ts,
                nodes, tasks_per_node, mem, time):
    data_prefix = write_data(num_total_real, coors_flakes_all, coors_inclusions, L_box, seed)
    in_prefix, all_prefix = write_in(data_prefix, sigma, num_cycle, ts)
    write_sh(in_prefix, all_prefix, nodes, tasks_per_node, mem, time)
    return data_prefix, in_prefix, all_prefix


def write_data(num_total_real, coors_flakes_all, coors_inclusions, L_box, seed, mass_inc=1.0):
    num_C_atoms, num_inc = len(coors_flakes_all), len(coors_inclusions)
    data_prefix = f'f_{num_total_real}_i_{num_inc}_s_{seed}'
    with open(f'data.{data_prefix}', 'w') as f:
        f.write('# \n')
        f.write('\n')
        f.write(f'{num_C_atoms + num_inc} atoms\n')
        f.write('0 bonds\n')
        f.write('0 angles\n')
        f.write('0 dihedrals\n')
        f.write('\n')
        f.write('2 atom types\n')
        f.write(f'{-L_box/2:.3f} {L_box/2:.3f} xlo xhi\n')
        f.write(f'{-L_box/2:.3f} {L_box/2:.3f} ylo yhi\n')
        f.write(f'{-L_box/2:.3f} {L_box/2:.3f} zlo zhi\n')
        f.write('\n')
        f.write('Masses\n')
        f.write('\n')
        f.write('1   12.01070\n')
        f.write(f'2   {mass_inc}\n')
        f.write('\n')
        f.write('Atoms\n')
        f.write('\n')
        for i, coor in enumerate(coors_flakes_all):
            f.write(f'{i + 1} 1 1 0 {coor[0]:.7f} {coor[1]:.7f} {coor[2]:.7f}\n')
        for i, coor in enumerate(coors_inclusions):
            f.write(f'{i + 1 + num_C_atoms} 2 2 0 {coor[0]:.7f} {coor[1]:.7f} {coor[2]:.7f}\n')
        return data_prefix


def write_in(data_prefix, sigma, num_cycle, ts, Tdrag=1, Pdrag=0.5):
    temperature = 3000.0
    in_prefix = f'sgm_{sigma}_c_{num_cycle}_t_{ts}'
    all_prefix = f'{data_prefix}_{in_prefix}'
    with open(f'in.{in_prefix}', 'w') as f:
        f.write('# \n')
        f.write('\n')
        f.write('units 		metal\n')
        f.write('timestep	0.5e-3\n')
        f.write('dimension 	3\n')
        f.write('boundary 	p p p\n')
        f.write(f'log 	log.{all_prefix}\n')
        f.write('\n')
        f.write('atom_style full\n')
        f.write(f'read_data 	data.{data_prefix}\n')
        f.write('group carbon type 1\n')
        f.write('group inclusions type 2\n')
        f.write('\n')
        f.write(f'pair_style hybrid airebo 3 lj/cut {sigma + 3} \n')
        f.write('pair_coeff	* * airebo CH.airebo C H\n')
        f.write(f'pair_coeff	1 2 lj/cut 0.652 {sigma}\n')
        f.write(f'pair_coeff	2 2 lj/cut 0.652 {sigma}\n')
        f.write('compute 	pe all pe\n')
        f.write('compute 	1 carbon stress/atom NULL pair\n')
        f.write('compute 	p all reduce sum c_1[*]\n')
        f.write('variable von equal 1e-25*c_p[1]\n')
        f.write('variable volume equal vol*1e-30\n')
        f.write('variable stress equal v_von/v_volume*1e-9\n')
        f.write('variable lengthx equal lx\n')
        f.write('\n')
        f.write('velocity 	all create 300 3 mom yes rot yes dist gaussian\n')
        f.write(f'fix		1 all npt temp 300.0 300.0 {Tdrag:.3f} iso 1 1000 {Pdrag:.3f}\n')
        f.write(f'dump       1 all custom 2000 {all_prefix}.lammpstrj id type x y z c_1[*]\n')
        f.write('thermo 		200\n')
        f.write('thermo_style    custom step temp press pe vol density lx ly lz xlo xhi v_stress\n')
        f.write('minimize 1.0e-4 1.0e-6 100 1000\n')
        f.write(f'run    {ts}\n')
        f.write('unfix 1\n')
        f.write(f'fix		1 all nvt temp 300.0 {temperature} {Tdrag:.3f}\n')
        f.write(f'run    {ts}\n')
        f.write('unfix 1\n')
        f.write(f'fix		1 all nvt temp {temperature} {temperature} {Tdrag:.3f}\n')
        f.write(f'run    {ts}\n')
        f.write('unfix 1\n')
        f.write(f'fix		1 all nvt temp {temperature} 300.0 {Tdrag:.3f}\n')
        f.write(f'run    {ts}\n')
        f.write('\n')
        for i in range(num_cycle - 1):
            f.write(f'# Cycle    {i + 2}\n')
            f.write('unfix 1\n')
            f.write(f'fix		1 all npt temp 300.0 300.0 {Tdrag:.3f} iso 1 1000 {Pdrag:.3f}\n')
            f.write('minimize 1.0e-4 1.0e-6 100 1000\n')
            f.write(f'run    {ts}\n')
            f.write('unfix 1\n')
            f.write(f'fix		1 all nvt temp 300.0 {temperature} {Tdrag:.3f}\n')
            f.write(f'run    {ts}\n')
            f.write('unfix 1\n')
            f.write(f'fix		1 all nvt temp {temperature} {temperature} {Tdrag:.3f}\n')
            f.write(f'run    {ts}\n')
            f.write('unfix 1\n')
            f.write(f'fix		1 all nvt temp {temperature} 300.0 {Tdrag:.3f}\n')
            f.write(f'run    {ts}\n')
            f.write('\n')
        f.write('delete_atoms group inclusions\n')
        # f.write('unfix 1\n')
        # f.write(f'fix		1 all npt temp 300.0 300.0 {Tdrag:.3f} iso 1 1000 {Pdrag:.3f}\n')
        # f.write('minimize 1.0e-4 1.0e-6 100 1000\n')
        # f.write(f'run    {ts}\n')
        f.write(f'write_data data.{all_prefix}\n')
    return in_prefix, all_prefix

def write_sh(in_prefix, all_prefix, nodes, tasks_per_node, mem, time):
    with open(f'sh.{all_prefix}', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write(f'#SBATCH --job-name="{all_prefix}"\n')
        f.write(f'#SBATCH --output="out.{all_prefix}"\n')
        f.write('#SBATCH --partition=compute\n')
        f.write('#SBATCH --constraint="lustre"\n')
        f.write(f'#SBATCH --nodes={nodes}\n')
        f.write(f'#SBATCH --ntasks-per-node={tasks_per_node}\n')
        f.write(f'#SBATCH --mem={mem}G\n')
        f.write('#SBATCH --account="ucb312"\n')
        f.write('#SBATCH --export=ALL\n')
        f.write(f'#SBATCH -t {time}:00:00\n')
        f.write('\n')
        f.write('module load   slurm\n')
        f.write('module load   gcc/10.2.0\n')
        f.write('module load   openmpi/4.0.4\n')
        f.write('module load   lammps/20200721-openblas\n')
        f.write('\n')
        f.write(f'srun lmp -in in.{in_prefix}\n')


