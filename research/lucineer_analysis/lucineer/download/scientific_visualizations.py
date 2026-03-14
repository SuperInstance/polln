#!/usr/bin/env python3
"""
Scientific Visualization Suite for Mask-Locked Inference Chip
=============================================================

Generates publication-quality figures for:
1. Thermal distribution maps
2. PDN impedance plots
3. Energy landscape visualizations
4. Noise analysis charts
5. Electromigration reliability curves
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import json
import os

# Set publication style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Custom colormap for thermal
thermal_colors = ['#000080', '#0000FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF8000', '#FF0000', '#FF00FF']
thermal_cmap = LinearSegmentedColormap.from_list('thermal', thermal_colors, N=256)


def create_thermal_visualization(output_dir: str = "."):
    """Generate thermal physics visualizations."""
    
    print("Generating thermal visualization...")
    
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Power density map
    ax1 = fig.add_subplot(gs[0, 0])
    
    # Generate power map data
    n_pe = 32
    power_map = np.ones((n_pe, n_pe)) * 0.5e-3  # 0.5mW per PE
    
    # Add thermal gradients
    for i in range(n_pe):
        for j in range(n_pe):
            edge_factor = 1.0 - 0.3 * min(i, j, n_pe-1-i, n_pe-1-j) / (n_pe//2)
            power_map[i, j] *= edge_factor
    
    # Add hotspots
    center = (n_pe//2, n_pe//2)
    for i in range(n_pe):
        for j in range(n_pe):
            dist = np.sqrt((i - center[0])**2 + (j - center[1])**2)
            if dist < 5:
                power_map[i, j] *= 2.0 * (1 - dist/5)
    
    im1 = ax1.imshow(power_map * 1000, cmap='hot', aspect='equal')
    ax1.set_xlabel('PE Column')
    ax1.set_ylabel('PE Row')
    ax1.set_title('(a) Power Density Distribution (mW)')
    plt.colorbar(im1, ax=ax1, label='Power (mW)')
    
    # 2. Thermal resistance network
    ax2 = fig.add_subplot(gs[0, 1])
    
    # Thermal resistance values
    components = ['Junction\n(Si)', 'Die Attach', 'Package', 'Heatsink', 'Ambient']
    r_values = [0.5, 2.0, 15.0, 5.0, 10.0]
    colors = ['#FF4444', '#FF8800', '#FFFF00', '#88FF00', '#00FF88']
    
    bars = ax2.bar(components, r_values, color=colors, edgecolor='black', linewidth=1)
    ax2.set_ylabel('Thermal Resistance (K/W)')
    ax2.set_title('(b) Thermal Resistance Network')
    ax2.set_ylim(0, 20)
    
    # Add value labels
    for bar, val in zip(bars, r_values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val:.1f}', ha='center', va='bottom', fontsize=9)
    
    # 3. Temperature vs Power
    ax3 = fig.add_subplot(gs[1, 0])
    
    power_range = np.linspace(0, 10, 100)  # W
    r_total = 32.5  # K/W
    t_ambient = 300  # K
    
    temp = t_ambient + power_range * r_total
    
    ax3.plot(power_range, temp, 'b-', linewidth=2, label='Junction Temperature')
    ax3.axhline(y=400, color='r', linestyle='--', label='Safe Limit (400K)')
    ax3.axhline(y=350, color='orange', linestyle='--', label='Target (350K)')
    ax3.fill_between(power_range, 350, 400, alpha=0.2, color='orange')
    
    ax3.set_xlabel('Total Power (W)')
    ax3.set_ylabel('Junction Temperature (K)')
    ax3.set_title('(c) Temperature vs Power Dissipation')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, 10)
    ax3.set_ylim(290, 450)
    
    # 4. Temperature profile along die
    ax4 = fig.add_subplot(gs[1, 1])
    
    x = np.linspace(0, 5, 100)  # mm
    center_temp = 380
    edge_temp = 340
    
    # Parabolic profile (simplified heat equation solution)
    temp_profile = center_temp - (center_temp - edge_temp) * (x / 2.5 - 1)**2
    
    ax4.plot(x, temp_profile, 'r-', linewidth=2)
    ax4.fill_between(x, temp_profile, 300, alpha=0.3, color='red')
    ax4.axhline(y=350, color='orange', linestyle='--', label='Target')
    
    ax4.set_xlabel('Position across die (mm)')
    ax4.set_ylabel('Temperature (K)')
    ax4.set_title('(d) Temperature Profile Across Die')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('Thermal Physics Analysis - Mask-Locked Inference Chip', fontsize=14, fontweight='bold')
    
    output_path = os.path.join(output_dir, 'thermal_physics_analysis.png')
    plt.savefig(output_path)
    plt.close()
    
    print(f"   Saved: {output_path}")
    return output_path


def create_circuit_visualization(output_dir: str = "."):
    """Generate circuit physics visualizations."""
    
    print("Generating circuit visualization...")
    
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Ternary inverter transfer curve
    ax1 = fig.add_subplot(gs[0, 0])
    
    v_in = np.linspace(0, 1.0, 500)
    v_out = np.zeros_like(v_in)
    
    # Simplified ternary inverter behavior
    for i, v in enumerate(v_in):
        if v < 0.35:
            v_out[i] = 1.0
        elif v < 0.65:
            v_out[i] = 0.5
        else:
            v_out[i] = 0
    
    # Smooth transitions
    v_out = np.convolve(v_out, np.ones(20)/20, mode='same')
    
    ax1.plot(v_in, v_out, 'b-', linewidth=2, label='Transfer Curve')
    ax1.axhline(y=0.25, color='gray', linestyle=':', alpha=0.5)
    ax1.axhline(y=0.75, color='gray', linestyle=':', alpha=0.5)
    ax1.axvline(x=0.25, color='gray', linestyle=':', alpha=0.5)
    ax1.axvline(x=0.75, color='gray', linestyle=':', alpha=0.5)
    
    # Noise margins
    nm_high = 0.75 - 0.65
    nm_mid = min(0.65 - 0.35, 0.75 - 0.25)
    
    ax1.fill_between([0.35, 0.65], [0.75, 0.75], [0.5, 0.5], alpha=0.3, color='green', label=f'NM_mid = {nm_mid:.2f}V')
    ax1.fill_between([0, 0.35], [1.0, 1.0], [0.75, 0.75], alpha=0.3, color='blue', label=f'NM_high = {nm_high:.2f}V')
    
    ax1.set_xlabel('Input Voltage (V)')
    ax1.set_ylabel('Output Voltage (V)')
    ax1.set_title('(a) Ternary Inverter Transfer Characteristic')
    ax1.legend(loc='center right', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1.1)
    
    # 2. Energy comparison: RAU vs MAC
    ax2 = fig.add_subplot(gs[0, 1])
    
    operations = ['RAU\n(Rotate)', 'RAU\n(Accum)', 'RAU\n(Total)', 'MAC\n(Multiply)', 'MAC\n(Accum)', 'MAC\n(Total)']
    energy_fj = [5, 8, 13, 90, 8, 98]
    colors = ['#00AAFF', '#00AAFF', '#0066FF', '#FF6600', '#FF6600', '#FF0000']
    
    bars = ax2.bar(operations, energy_fj, color=colors, edgecolor='black', linewidth=1)
    ax2.set_ylabel('Energy per Operation (fJ)')
    ax2.set_title('(b) Energy: RAU vs MAC (8-bit)')
    ax2.set_yscale('log')
    ax2.set_ylim(1, 200)
    
    # Add ratio annotation
    ax2.annotate('', xy=(2, 98), xytext=(2, 13),
                arrowprops=dict(arrowstyle='<->', color='green', lw=2))
    ax2.text(2.3, 30, '7.5×\nsavings', fontsize=10, color='green', fontweight='bold')
    
    # 3. Wire delay vs length
    ax3 = fig.add_subplot(gs[1, 0])
    
    length_mm = np.linspace(0.1, 5, 50)
    
    # RC delay model
    rho = 2.2e-8  # Ω·m
    c_per_mm = 200e-15  # F/mm
    r_per_mm = 50  # Ω/mm
    
    delay_ps = r_per_mm * c_per_mm * length_mm * 1e12 * length_mm / 2  # Distributed RC
    
    ax3.semilogy(length_mm, delay_ps, 'b-', linewidth=2, label='RC Delay')
    ax3.axhline(y=100, color='r', linestyle='--', label='100ps Budget')
    ax3.axhline(y=10, color='orange', linestyle='--', label='10ps Target')
    
    ax3.set_xlabel('Wire Length (mm)')
    ax3.set_ylabel('Delay (ps)')
    ax3.set_title('(c) Interconnect Delay vs Length')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Ternary weight resistance encoding
    ax4 = fig.add_subplot(gs[1, 1])
    
    weights = ['-1', '0', '+1']
    resistances = [550, float('inf'), 50]  # Ω
    display_r = [550, 1000, 50]  # For visualization
    
    colors = ['#FF4444', '#888888', '#44FF44']
    bars = ax4.bar(weights, display_r, color=colors, edgecolor='black', linewidth=1)
    
    ax4.set_ylabel('Effective Resistance (Ω)')
    ax4.set_xlabel('Weight Value')
    ax4.set_title('(d) Ternary Weight Resistance Encoding')
    
    # Add annotations
    ax4.text(0, 560, 'Inv. path\n(+500Ω)', ha='center', fontsize=9)
    ax4.text(1, 1010, 'Open\n(∞Ω)', ha='center', fontsize=9)
    ax4.text(2, 55, 'Direct\n(50Ω)', ha='center', fontsize=9)
    
    plt.suptitle('Circuit Physics Analysis - Mask-Locked Inference Chip', fontsize=14, fontweight='bold')
    
    output_path = os.path.join(output_dir, 'circuit_physics_analysis.png')
    plt.savefig(output_path)
    plt.close()
    
    print(f"   Saved: {output_path}")
    return output_path


def create_em_noise_visualization(output_dir: str = "."):
    """Generate electromagnetic and noise visualizations."""
    
    print("Generating EM and noise visualization...")
    
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. PDN impedance vs frequency
    ax1 = fig.add_subplot(gs[0, 0])
    
    freq = np.logspace(3, 10, 200)
    
    # Simplified PDN impedance model
    z_vrm = 1e-3 + 1j * 2 * np.pi * freq * 1e-6
    z_pcb = 1e-3 + 1j * 2 * np.pi * freq * 1e-9
    z_pkg = 5e-3 + 1j * 2 * np.pi * freq * 100e-12
    
    # Decoupling capacitors
    z_decap = np.zeros_like(freq, dtype=complex)
    for c in [1e-6, 100e-9, 10e-9]:
        z_c = 0.01 + 1j * (2 * np.pi * freq * 100e-12 - 1/(2 * np.pi * freq * c + 1e-20))
        z_decap = z_decap + 1/(z_c + 1e-20)
    z_decap = 1/(z_decap + 1e-20)
    
    z_total = np.abs(z_vrm + z_pcb + z_pkg + z_decap)
    
    ax1.loglog(freq, z_total, 'b-', linewidth=2, label='Total Impedance')
    ax1.axhline(y=0.1, color='r', linestyle='--', label='Target (100mΩ)')
    ax1.axvline(x=1e9, color='gray', linestyle=':', alpha=0.5, label='1 GHz')
    
    # Mark resonance
    min_idx = np.argmin(z_total)
    ax1.plot(freq[min_idx], z_total[min_idx], 'ro', markersize=10, label=f'Resonance: {freq[min_idx]/1e6:.0f} MHz')
    
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Impedance (Ω)')
    ax1.set_title('(a) Power Distribution Network Impedance')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(1e3, 1e10)
    ax1.set_ylim(1e-3, 100)
    
    # 2. Crosstalk vs spacing
    ax2 = fig.add_subplot(gs[0, 1])
    
    spacing_nm = np.linspace(50, 300, 50)
    pitch = 90  # nm
    
    c_coupling = pitch / spacing_nm  # Normalized
    k_crosstalk = c_coupling / (1 + c_coupling)
    
    ax2.plot(spacing_nm, k_crosstalk * 100, 'g-', linewidth=2)
    ax2.axhline(y=10, color='r', linestyle='--', label='10% Threshold')
    ax2.axvline(x=180, color='gray', linestyle=':', alpha=0.5, label='2× Pitch')
    
    ax2.set_xlabel('Wire Spacing (nm)')
    ax2.set_ylabel('Crosstalk Coefficient (%)')
    ax2.set_title('(b) Crosstalk vs Wire Spacing')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Noise spectral density
    ax3 = fig.add_subplot(gs[1, 0])
    
    freq_noise = np.logspace(0, 10, 500)
    
    # Thermal noise (flat)
    s_thermal = np.ones_like(freq_noise) * 4e-9  # V²/Hz (normalized)
    
    # Shot noise (flat)
    s_shot = np.ones_like(freq_noise) * 3.2e-19  # A²/Hz
    
    # Flicker noise (1/f)
    s_flicker = 1e-6 / freq_noise
    
    ax3.loglog(freq_noise, s_thermal, 'b-', linewidth=2, label='Thermal')
    ax3.loglog(freq_noise, s_flicker, 'r-', linewidth=2, label='Flicker (1/f)')
    ax3.axvline(x=1e6, color='gray', linestyle=':', alpha=0.5, label='1 MHz corner')
    
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Noise PSD (V²/Hz)')
    ax3.set_title('(c) Noise Spectral Density')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Ternary noise margins
    ax4 = fig.add_subplot(gs[1, 1])
    
    noise_sigma = np.linspace(0, 100, 100)  # mV
    
    # Error probability for ternary levels
    from scipy.stats import norm
    
    vdd = 1.0  # V
    threshold = vdd / 4  # 250mV
    
    ber_level0 = 2 * norm.cdf(-threshold / (noise_sigma * 1e-3))
    ber_level1 = 4 * norm.cdf(-threshold / (noise_sigma * 1e-3))  # Two thresholds
    ber_level2 = ber_level0
    
    ax4.semilogy(noise_sigma, ber_level0, 'b-', linewidth=2, label='Level 0/2')
    ax4.semilogy(noise_sigma, ber_level1, 'r-', linewidth=2, label='Level 1 (middle)')
    ax4.axhline(y=1e-12, color='green', linestyle='--', label='Target BER (10⁻¹²)')
    ax4.axvline(x=50, color='orange', linestyle=':', label='50mV noise')
    
    ax4.set_xlabel('Noise RMS (mV)')
    ax4.set_ylabel('Bit Error Rate')
    ax4.set_title('(d) Ternary Logic Error Rate vs Noise')
    ax4.legend(loc='upper right', fontsize=8)
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(1e-20, 1)
    
    plt.suptitle('Electromagnetic & Noise Analysis - Mask-Locked Inference Chip', fontsize=14, fontweight='bold')
    
    output_path = os.path.join(output_dir, 'em_noise_analysis.png')
    plt.savefig(output_path)
    plt.close()
    
    print(f"   Saved: {output_path}")
    return output_path


def create_reliability_visualization(output_dir: str = "."):
    """Generate reliability and materials science visualizations."""
    
    print("Generating reliability visualization...")
    
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Electromigration MTTF
    ax1 = fig.add_subplot(gs[0, 0])
    
    j = np.logspace(4, 7, 100)  # A/cm²
    
    # Black's equation
    E_a = 0.7  # eV
    k_B = 8.617e-5  # eV/K
    T = 350  # K
    
    mttf_100nm = 1e5 * j**(-2) * np.exp(E_a / (k_B * T)) / 1e4  # years (scaled)
    mttf_50nm = mttf_100nm * 0.5  # Short line effect
    mttf_20nm = mttf_100nm * 0.1  # Stronger short line
    
    ax1.loglog(j / 1e6, mttf_100nm, 'b-', linewidth=2, label='100nm line')
    ax1.loglog(j / 1e6, mttf_50nm, 'g-', linewidth=2, label='50nm line')
    ax1.loglog(j / 1e6, mttf_20nm, 'r-', linewidth=2, label='20nm line')
    
    ax1.axhline(y=10, color='gray', linestyle='--', label='10 year target')
    ax1.axvline(x=1, color='orange', linestyle=':', label='1 MA/cm²')
    
    ax1.set_xlabel('Current Density (MA/cm²)')
    ax1.set_ylabel('MTTF (years)')
    ax1.set_title('(a) Electromigration Reliability')
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0.01, 10)
    ax1.set_ylim(0.1, 1e6)
    
    # 2. Temperature coefficient of resistance
    ax2 = fig.add_subplot(gs[0, 1])
    
    T_range = np.linspace(250, 450, 100)  # K
    rho_0 = 2.2e-8  # Ω·m at 300K
    alpha = 0.00393  # /K
    
    rho_T = rho_0 * (1 + alpha * (T_range - 300))
    
    ax2.plot(T_range - 273, rho_T * 1e8, 'b-', linewidth=2)
    ax2.axvline(x=25, color='green', linestyle='--', label='25°C nominal')
    ax2.axvline(x=100, color='orange', linestyle='--', label='100°C operating')
    
    ax2.set_xlabel('Temperature (°C)')
    ax2.set_ylabel('Resistivity (μΩ·cm)')
    ax2.set_title('(b) Copper Resistivity vs Temperature')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Energy landscape
    ax3 = fig.add_subplot(gs[1, 0])
    
    # Generate energy landscape for ternary weights
    n_weights = 1000
    n_samples = 10000
    
    energies = []
    for _ in range(n_samples):
        weights = np.random.choice([-1, 0, 1], size=n_weights, p=[0.25, 0.5, 0.25])
        inputs = np.random.choice([-1, 1], size=n_weights)
        e = -np.sum(weights * inputs)  # Ising-like energy
        energies.append(e)
    
    ax3.hist(energies, bins=50, density=True, color='steelblue', edgecolor='black', alpha=0.7)
    
    # Fit Gaussian
    from scipy.stats import norm
    mu, sigma = norm.fit(energies)
    x = np.linspace(min(energies), max(energies), 100)
    ax3.plot(x, norm.pdf(x, mu, sigma), 'r-', linewidth=2, label=f'Gaussian fit\nμ={mu:.0f}, σ={sigma:.0f}')
    
    ax3.set_xlabel('Energy')
    ax3.set_ylabel('Probability Density')
    ax3.set_title('(c) Energy Landscape for Ternary Weights')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Thermodynamic computation limits
    ax4 = fig.add_subplot(gs[1, 1])
    
    T_thermo = np.linspace(200, 500, 100)
    k_B = 1.38e-23  # J/K
    
    landauer = k_B * T_thermo * np.log(2)  # J
    
    # Compare to CMOS
    cmos_energy = 1e-15  # J (1 fJ typical)
    
    ax4.semilogy(T_thermo - 273, landauer, 'b-', linewidth=2, label='Landauer limit')
    ax4.axhline(y=cmos_energy, color='r', linestyle='--', label='Current CMOS (~1 fJ)')
    ax4.axvline(x=350-273, color='orange', linestyle=':', label='350K operating temp')
    
    ax4.set_xlabel('Temperature (°C)')
    ax4.set_ylabel('Energy per Bit (J)')
    ax4.set_title('(d) Thermodynamic Computation Limits')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('Reliability & Materials Science Analysis - Mask-Locked Inference Chip', fontsize=14, fontweight='bold')
    
    output_path = os.path.join(output_dir, 'reliability_analysis.png')
    plt.savefig(output_path)
    plt.close()
    
    print(f"   Saved: {output_path}")
    return output_path


def create_comprehensive_dashboard(output_dir: str = "."):
    """Create a comprehensive dashboard combining all simulations."""
    
    print("Generating comprehensive dashboard...")
    
    fig = plt.figure(figsize=(20, 14))
    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.3)
    
    # Row 1: Thermal
    # Power map
    ax1 = fig.add_subplot(gs[0, 0])
    n_pe = 32
    power_map = np.ones((n_pe, n_pe)) * 0.5e-3
    for i in range(n_pe):
        for j in range(n_pe):
            edge_factor = 1.0 - 0.3 * min(i, j, n_pe-1-i, n_pe-1-j) / (n_pe//2)
            power_map[i, j] *= edge_factor
    im1 = ax1.imshow(power_map * 1000, cmap='hot', aspect='equal')
    ax1.set_title('Power Density (mW)', fontsize=10)
    plt.colorbar(im1, ax=ax1, shrink=0.8)
    
    # Temperature profile
    ax2 = fig.add_subplot(gs[0, 1])
    power_range = np.linspace(0, 10, 100)
    temp = 300 + power_range * 32.5
    ax2.plot(power_range, temp, 'b-', linewidth=2)
    ax2.axhline(y=400, color='r', linestyle='--')
    ax2.fill_between(power_range, 350, 400, alpha=0.2, color='orange')
    ax2.set_xlabel('Power (W)')
    ax2.set_ylabel('Temp (K)')
    ax2.set_title('Temperature vs Power', fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # RAU energy
    ax3 = fig.add_subplot(gs[0, 2])
    ops = ['RAU', 'MAC']
    energy = [13, 98]
    colors = ['#00AAFF', '#FF4444']
    ax3.bar(ops, energy, color=colors, edgecolor='black')
    ax3.set_ylabel('Energy (fJ)')
    ax3.set_title('RAU vs MAC Energy', fontsize=10)
    ax3.annotate('7.5× savings', xy=(0.5, 50), ha='center', fontsize=9, color='green')
    
    # Ternary transfer
    ax4 = fig.add_subplot(gs[0, 3])
    v_in = np.linspace(0, 1, 200)
    v_out = np.zeros_like(v_in)
    v_out[:70] = 1.0
    v_out[70:130] = 0.5
    v_out[130:] = 0
    v_out = np.convolve(v_out, np.ones(10)/10, mode='same')
    ax4.plot(v_in, v_out, 'b-', linewidth=2)
    ax4.set_xlabel('Vin (V)')
    ax4.set_ylabel('Vout (V)')
    ax4.set_title('Ternary Inverter', fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    # Row 2: EM & Signal Integrity
    # PDN impedance
    ax5 = fig.add_subplot(gs[1, 0])
    freq = np.logspace(3, 10, 100)
    z = 0.01 + 1j * 2 * np.pi * freq * 1e-9
    ax5.loglog(freq, np.abs(z), 'b-', linewidth=2)
    ax5.axhline(y=0.1, color='r', linestyle='--')
    ax5.set_xlabel('Freq (Hz)')
    ax5.set_ylabel('Z (Ω)')
    ax5.set_title('PDN Impedance', fontsize=10)
    ax5.grid(True, alpha=0.3)
    
    # Crosstalk
    ax6 = fig.add_subplot(gs[1, 1])
    spacing = np.linspace(50, 300, 50)
    k_ct = (90 / spacing) / (1 + 90 / spacing)
    ax6.plot(spacing, k_ct * 100, 'g-', linewidth=2)
    ax6.axhline(y=10, color='r', linestyle='--')
    ax6.set_xlabel('Spacing (nm)')
    ax6.set_ylabel('Crosstalk (%)')
    ax6.set_title('Crosstalk Coefficient', fontsize=10)
    ax6.grid(True, alpha=0.3)
    
    # Wire delay
    ax7 = fig.add_subplot(gs[1, 2])
    length = np.linspace(0.1, 5, 50)
    delay = 50 * 200e-15 * length**2 * 1e12 / 2
    ax7.semilogy(length, delay, 'b-', linewidth=2)
    ax7.axhline(y=100, color='r', linestyle='--')
    ax7.set_xlabel('Length (mm)')
    ax7.set_ylabel('Delay (ps)')
    ax7.set_title('Interconnect Delay', fontsize=10)
    ax7.grid(True, alpha=0.3)
    
    # Noise
    ax8 = fig.add_subplot(gs[1, 3])
    sigma = np.linspace(0, 100, 100)
    from scipy.stats import norm
    ber = 2 * norm.cdf(-0.25 / (sigma * 1e-3 + 1e-20))
    ax8.semilogy(sigma, ber, 'b-', linewidth=2)
    ax8.axhline(y=1e-12, color='green', linestyle='--')
    ax8.set_xlabel('Noise (mV)')
    ax8.set_ylabel('BER')
    ax8.set_title('Error Rate vs Noise', fontsize=10)
    ax8.grid(True, alpha=0.3)
    
    # Row 3: Reliability & Physics
    # EM MTTF
    ax9 = fig.add_subplot(gs[2, 0])
    j = np.logspace(4, 7, 50)
    mttf = 1e5 * j**(-2) * np.exp(0.7 / (8.617e-5 * 350)) / 1e4
    ax9.loglog(j/1e6, mttf, 'b-', linewidth=2)
    ax9.axhline(y=10, color='gray', linestyle='--')
    ax9.set_xlabel('J (MA/cm²)')
    ax9.set_ylabel('MTTF (years)')
    ax9.set_title('EM Reliability', fontsize=10)
    ax9.grid(True, alpha=0.3)
    
    # Resistivity vs T
    ax10 = fig.add_subplot(gs[2, 1])
    T = np.linspace(250, 450, 100)
    rho = 2.2e-8 * (1 + 0.00393 * (T - 300))
    ax10.plot(T-273, rho*1e8, 'b-', linewidth=2)
    ax10.axvline(x=100, color='orange', linestyle='--')
    ax10.set_xlabel('T (°C)')
    ax10.set_ylabel('ρ (μΩ·cm)')
    ax10.set_title('Resistivity vs Temp', fontsize=10)
    ax10.grid(True, alpha=0.3)
    
    # Energy landscape
    ax11 = fig.add_subplot(gs[2, 2])
    energies = []
    for _ in range(5000):
        w = np.random.choice([-1, 0, 1], size=1000, p=[0.25, 0.5, 0.25])
        x = np.random.choice([-1, 1], size=1000)
        energies.append(-np.sum(w * x))
    ax11.hist(energies, bins=30, density=True, color='steelblue', edgecolor='black', alpha=0.7)
    ax11.set_xlabel('Energy')
    ax11.set_ylabel('Density')
    ax11.set_title('Energy Landscape', fontsize=10)
    
    # Landauer limit
    ax12 = fig.add_subplot(gs[2, 3])
    T_land = np.linspace(200, 500, 100)
    landauer = 1.38e-23 * T_land * np.log(2)
    ax12.semilogy(T_land-273, landauer, 'b-', linewidth=2)
    ax12.axhline(y=1e-15, color='r', linestyle='--')
    ax12.set_xlabel('T (°C)')
    ax12.set_ylabel('E/bit (J)')
    ax12.set_title('Landauer Limit', fontsize=10)
    ax12.grid(True, alpha=0.3)
    
    plt.suptitle('MASK-LOCKED INFERENCE CHIP\nComprehensive Scientific Simulation Dashboard', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    output_path = os.path.join(output_dir, 'comprehensive_science_dashboard.png')
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    
    print(f"   Saved: {output_path}")
    return output_path


def main():
    """Generate all visualizations."""
    
    output_dir = "."
    
    print("=" * 60)
    print("SCIENTIFIC VISUALIZATION SUITE")
    print("=" * 60)
    
    outputs = []
    
    outputs.append(create_thermal_visualization(output_dir))
    outputs.append(create_circuit_visualization(output_dir))
    outputs.append(create_em_noise_visualization(output_dir))
    outputs.append(create_reliability_visualization(output_dir))
    outputs.append(create_comprehensive_dashboard(output_dir))
    
    print("\n" + "=" * 60)
    print("VISUALIZATION COMPLETE")
    print("=" * 60)
    print("\nGenerated files:")
    for out in outputs:
        print(f"  - {out}")
    
    return outputs


if __name__ == "__main__":
    main()
