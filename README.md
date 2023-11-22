# Vinyasa CLI

Vinyasa is a Python-based command-line interface (CLI) tool designed to streamline 
the execution of multiple scripts in sequence (like a pipeline), 
with added features for caching and pipeline history tracking.

<p align="center">
  <img src="cover.png" width="250"/>
</p>



## Features

- **Sequential Script Execution**: Run multiple Python scripts in sequence.
- **Caching**: Cache the results of function calls to improve efficiency. Changes in the operational structure and logic of functions will invalidate the cache.
- **History Tracking**: Keep a record of script execution sequences.
- **Clear Cache and History**: Easily clear cached data and execution history.

Certainly! Here's an additional section for the README, explaining the origin of the name and detailing the caching mechanism:

## Origin of the Name

The name "Vinyasa" is inspired by the concept of Vinyasa in yoga, 
which refers to a smooth transition between asanas (poses), 
emphasizing fluidity and connected sequences. 
Similarly, Vinyasa CLI seamlessly transitions between scripts, maintaining a flow in computational processes.

## Caching Mechanism

Vinyasa utilizes a bytecode-based caching mechanism. 
This means the cache is keyed on the operational structure and logic of functions, not merely on variable values or textual changes. 
This approach ensures that any functional changes to the code will result in cache invalidation, 
thereby rerunning the function with updated logic. 
This method is efficient for detecting substantial changes in function behavior, enhancing overall execution efficiency.

## Installation

To install Vinyasa, clone the repository and install the dependencies:

```bash
git clone https://github.com/KikeM/vinyasa
cd vinyasa
pip install .
```

## Usage

Run a sequence of scripts:

```bash
vinyasa run load_data.py process_data.py plot_data.py
```

View execution history:

```bash
vinyasa history
```

Clear the history:

```bash
vinyasa history --clear
```

Dump history to a file:

```bash
vinyasa history --dump history_dump.txt
```

Clear all cached function results:

```bash
vinyasa clear
```

## Examples
Using the scripts in the `examples` directory, we can see how `vinyasa` and the cache work.

First, we run the scripts `first_slow_operation.py` and `reusing_results_from_previous_steps.py`:
```
(.venv) $ vinyasa run examples/first_slow_operation.py examples/reusing_results_from_previous_steps.py 
```

We can see that the first script takes a long time to run, but the second script runs very quickly.
```
I am a script that takes a long time to run! Please cache me!
Loading data...
Data loaded!
5
I am a script that reuses the results from previous steps!
a=5
a=25
(pipeline) Execution time: 5.01 seconds (0.08 minutes)
```

Now, let's run the same scripts again:
```
(.venv) $ vinyasa run examples/first_slow_operation.py examples/reusing_results_from_previous_steps.py
```

This time, we can see that the first script runs very quickly, since the results are cached.
```
(.venv) $ vinyasa run examples/first_slow_operation.py examples/reusing_results_from_previous_steps.py 
I am a script that takes a long time to run! Please cache me!
Reading from cache: /tmp/vinyasa/012a44b6baab9d52fd622fe540194daa2f9d9744fb71f16b685ff1a51381c0d3.pkl for load_data
5
I am a script that reuses the results from previous steps!
a=5
a=25

(pipeline) Execution time: 0.00 seconds (0.00 minutes)
```

## Contributing

Contributions to Vinyasa are welcome! Please read our contributing guidelines for details on how to submit contributions.