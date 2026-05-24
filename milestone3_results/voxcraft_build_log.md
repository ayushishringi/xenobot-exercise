# VoxCraft-sim Build Attempt Log

## Environment

I attempted to run VoxCraft-sim in Google Colab using a T4 GPU because my local machine is an Apple M4 Mac and does not have an NVIDIA CUDA GPU.

The Colab GPU was verified with:

```bash
nvidia-smi
```


The runtime showed a Tesla T4 GPU with CUDA support.

### Build steps attempted

I cloned the official VoxCraft-sim repository:

git clone https://github.com/voxcraft/voxcraft-sim.git

I installed build dependencies:

apt-get update
apt-get install -y cmake build-essential libboost-all-dev

I configured the project with CMake:

cd voxcraft-sim
mkdir build
cd build
cmake ..

CMake successfully detected:

GNU C++ compiler
NVIDIA CUDA compiler
Boost filesystem, thread, chrono, and program_options
CUDA architecture for the Tesla T4 GPU

### Partial build success

The main launcher executable was built successfully:

voxcraft-sim/build/voxcraft-sim

Running the launcher displayed the expected Voxelyze3 usage message with options such as:

-i <input directory>
-o <output report>
-l
-f

The demo input file was also found:

voxcraft-sim/demos/basic/base.vxa
### Issue encountered

The required simulation worker executable vx3_node_worker did not build successfully. The build failed in the Voxelyze CUDA source files with errors involving calls to cudaDeviceSynchronize() from device functions.

The main error was:

calling a __host__ function("cudaDeviceSynchronize") from a __device__ function is not allowed

There were also Boost.Asio compilation errors in the Colab CUDA 12.8 / Boost environment.

Because the worker executable was not produced, the simulator launcher could not run the demo .vxa file. The launcher reported:

Need an executable worker but nothing found.
### Conclusion

A real VoxCraft-sim build was attempted in a GPU-enabled environment. The main VoxCraft-sim launcher built and ran, but the required worker executable failed to compile because of CUDA/Boost compatibility issues in the available Colab environment.

For this reason, the project keeps a simulator adapter and fallback displacement-style evaluation for local experiments. The fallback simulator is not claimed to be real VoxCraft-sim physics, but it allowed the evolutionary pipeline, ablation study, and multi-objective experiments to be tested.