import numpy as np
import matplotlib.pyplot as plt

# Technology parameters for 28nm
tech_params = {
    'Vdd': 0.9,  # V
    'Vth': 0.4,  # V
    'I_leak': 1e-6,  # A
    'C_gate': 1e-15,  # F
    'C_wire': 1e-15,  # F
    'alpha': 0.1,  # activity factor for switching power
    'beta': 0.5,  # activity factor for leakage power
    'f_clk': 1e9,  # Hz
    'P_mem_sram': 1e-6,  # W
    'P_mem_rom': 1e-6,  # W
    'P_clk_tree': 1e-6  # W
}

# Function to estimate activity factor
def estimate_activity_factor(activity_patterns):
    return np.mean(activity_patterns)

# Function to calculate switching power
def calculate_switching_power(array_size, frequency, voltage, activity_factor):
    return 0.5 * array_size * frequency * voltage**2 * activity_factor * tech_params['C_gate']

# Function to estimate leakage power
def estimate_leakage_power(array_size, voltage, activity_factor):
    return array_size * voltage * tech_params['I_leak'] * activity_factor * tech_params['beta']

# Function to calculate memory power
def calculate_memory_power():
    return tech_params['P_mem_sram'] + tech_params['P_mem_rom']

# Function to calculate clock tree power
def calculate_clock_tree_power():
    return tech_params['P_clk_tree']

# Function to calculate total power
def calculate_total_power(switching_power, leakage_power, memory_power, clock_tree_power):
    return switching_power + leakage_power + memory_power + clock_tree_power

# Function to calculate efficiency metrics
def calculate_efficiency_metrics(total_power, array_size, frequency):
    return array_size * frequency / total_power

# Main function
def main():
    # Inputs
    array_size = 1024
    frequency = 1e9  # Hz
    voltage = 0.9  # V
    activity_patterns = np.random.rand(1000)

    # Estimate activity factor
    activity_factor = estimate_activity_factor(activity_patterns)

    # Calculate switching power
    switching_power = calculate_switching_power(array_size, frequency, voltage, activity_factor)

    # Estimate leakage power
    leakage_power = estimate_leakage_power(array_size, voltage, activity_factor)

    # Calculate memory power
    memory_power = calculate_memory_power()

    # Calculate clock tree power
    clock_tree_power = calculate_clock_tree_power()

    # Calculate total power
    total_power = calculate_total_power(switching_power, leakage_power, memory_power, clock_tree_power)

    # Calculate efficiency metrics
    efficiency_metrics = calculate_efficiency_metrics(total_power, array_size, frequency)

    # Print results
    print("Total Power: {:.2f} W".format(total_power))
    print("Switching Power: {:.2f} W".format(switching_power))
    print("Leakage Power: {:.2f} W".format(leakage_power))
    print("Memory Power: {:.2f} W".format(memory_power))
    print("Clock Tree Power: {:.2f} W".format(clock_tree_power))
    print("Efficiency Metrics: {:.2f} tok/s/W".format(efficiency_metrics))

    # Visualization
    labels = ['Switching Power', 'Leakage Power', 'Memory Power', 'Clock Tree Power']
    sizes = [switching_power, leakage_power, memory_power, clock_tree_power]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.title('Power Breakdown')
    plt.show()

    # Sensitivity analysis
    voltage_sweep = np.linspace(0.5, 1.5, 100)
    power_sweep = [calculate_switching_power(array_size, frequency, v, activity_factor) for v in voltage_sweep]
    plt.plot(voltage_sweep, power_sweep)
    plt.xlabel('Voltage (V)')
    plt.ylabel('Switching Power (W)')
    plt.title('Sensitivity Analysis')
    plt.show()

    # Optimization suggestions
    print("Optimization Suggestions:")
    print("1. Reduce voltage to minimize switching power.")
    print("2. Optimize activity factor to minimize leakage power.")
    print("3. Use low-power memory technologies to minimize memory power.")
    print("4. Optimize clock tree design to minimize clock tree power.")

if __name__ == "__main__":
    main()