#PBS -N HPL_short_run
#PBS -q simple_q
#PBS -l walltime=168:00:00
#PBS -l nodes=1:ppn=24
#PBS -V

cd $PBS_O_WORKDIR

NCPU=`wc -l < $PBS_NODEFILE`
NNODES=`uniq $PBS_NODEFILE | wc -l`

echo ------------------------------------------------------
echo ' This job is allocated on '${NCPU}' cpu(s)'
echo 'Job is running on node(s): '
cat $PBS_NODEFILE
echo ------------------------------------------------------
echo PBS: qsub is running on $PBS_O_HOST
echo PBS: originating queue is $PBS_O_QUEUE
echo PBS: executing queue is $PBS_QUEUE
echo PBS: working directory is $PBS_O_WORKDIR
echo PBS: execution mode is $PBS_ENVIRONMENT
echo PBS: job identifier is $PBS_JOBID
echo PBS: job name is $PBS_JOBNAME
echo PBS: node file is $PBS_NODEFILE
echo PBS: number of nodes is $NNODES
echo PBS: current home directory is $PBS_O_HOME
echo PBS: PATH = $PBS_O_PATH
echo ------------------------------------------------------

##For openmpi-intel
##export LD_LIBRARY_PATH=/share/apps/openmpi-1.8.8-intel/lib:$LD_LIBRARY_PATH
##export PATH=/share/apps/openmpi-1.8.8-intel/bin:$PATH

cat $PBS_NODEFILE >./hostfile
