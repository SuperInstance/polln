# Numerical Methods for POLLN Differential Equations

This document provides detailed explanations of numerical methods used to solve PDEs and SDEs in POLLN analysis.

## Table of Contents

1. [Finite Difference Methods](#1-finite-difference-methods)
2. [Spectral Methods](#2-spectral-methods)
3. [Finite Element Methods](#3-finite-element-methods)
4. [Stochastic Integration](#4-stochastic-integration)
5. [Adaptive Methods](#5-adaptive-methods)
6. [Parallel Computing](#6-parallel-computing)

---

## 1. Finite Difference Methods

### 1.1 Basic Concepts

Finite difference methods approximate derivatives using local function values:

```python
# First derivative approximations
def forward_diff(f, dx):
    """Forward difference: O(Δx)"""
    return (f[1:] - f[:-1]) / dx

def backward_diff(f, dx):
    """Backward difference: O(Δx)"""
    return (f[1:] - f[:-1]) / dx

def central_diff(f, dx):
    """Central difference: O(Δx²)"""
    return (f[2:] - f[:-2]) / (2 * dx)

# Second derivative (central)
def second_diff(f, dx):
    """Second derivative: O(Δx²)"""
    return (f[2:] - 2*f[1:-1] + f[:-2]) / dx**2
```

### 1.2 Laplacian in Multiple Dimensions

**2D 5-point stencil**:
```python
def laplacian_2d(f, dx):
    """Compute Laplacian using 5-point stencil"""
    return (
        np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
        np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) -
        4 * f
    ) / dx**2
```

**3D 7-point stencil**:
```python
def laplacian_3d(f, dx):
    """Compute Laplacian using 7-point stencil"""
    return (
        np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
        np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) +
        np.roll(f, 1, axis=2) + np.roll(f, -1, axis=2) -
        6 * f
    ) / dx**2
```

### 1.3 Time Stepping Schemes

#### Forward Euler (Explicit)
```python
def forward_euler(u, dt, rhs_func):
    """Forward Euler: u_new = u + dt * RHS(u)"""
    return u + dt * rhs_func(u)
```

**Stability**: Requires CFL condition `dt ≤ C * dx²`

#### Backward Euler (Implicit)
```python
def backward_euler(u, dt, rhs_func):
    """Backward Euler: u_new = u + dt * RHS(u_new)"""
    # Requires solving nonlinear system
    from scipy.optimize import fsolve
    def residual(u_new):
        return u_new - u - dt * rhs_func(u_new)
    return fsolve(residual, u)
```

**Stability**: Unconditionally stable

#### Crank-Nicolson (Semi-Implicit)
```python
def crank_nicolson(u, dt, rhs_func):
    """Crank-Nicolson: u_new = u + dt/2 * [RHS(u) + RHS(u_new)]"""
    # Second-order accurate, unconditionally stable
    from scipy.optimize import fsolve
    def residual(u_new):
        return u_new - u - (dt/2) * (rhs_func(u) + rhs_func(u_new))
    return fsolve(residual, u)
```

**Properties**:
- Second-order in time
- Unconditionally stable
- Conservative for linear systems

### 1.4 Stability Analysis

**Von Neumann stability analysis**:

For a scheme `u_j^{n+1} = G u_j^n`, amplification factor G:

```python
def analyze_stability(scheme_func, k_range, dt, dx):
    """Analyze stability using von Neumann method"""
    G_values = []
    for k in k_range:
        # Test mode u_j^n = G^n * exp(ikx)
        # Compute amplification factor G
        x = np.arange(100) * dx
        u = np.exp(1j * k * x)
        u_new = scheme_func(u, dt, dx)
        G = u_new[50] / u[50]  # Amplification factor
        G_values.append(abs(G))
    return np.array(G_values)
```

**CFL Condition**:
```latex
|G| ≤ 1 + CΔt  (Stability)
```

For diffusion: `Δt ≤ Δx²/(2D)`

---

## 2. Spectral Methods

### 2.1 Fourier Transform Methods

**FFT-based differentiation**:
```python
def spectral_derivative(f, dx, order=1):
    """Compute derivative using FFT"""
    N = len(f)
    f_hat = np.fft.fft(f)

    # Wave numbers
    k = 2 * np.pi * np.fft.fftfreq(N, d=dx)

    # Derivative in Fourier space
    if order == 1:
        df_hat = 1j * k * f_hat
    elif order == 2:
        df_hat = -k**2 * f_hat

    # Transform back
    df = np.real(np.fft.ifft(df_hat))
    return df
```

**Spectral Laplacian**:
```python
def spectral_laplacian(f, dx):
    """Compute Laplacian using FFT"""
    f_hat = np.fft.fft2(f)  # 2D FFT

    # Wave numbers
    kx = 2 * np.pi * np.fft.fftfreq(f.shape[0], d=dx)
    ky = 2 * np.pi * np.fft.fftfreq(f.shape[1], d=dx)
    KX, KY = np.meshgrid(kx, ky, indexing='ij')

    # Laplacian in Fourier space
    K2 = KX**2 + KY**2
    laplacian_hat = -K2 * f_hat

    # Transform back
    laplacian = np.real(np.fft.ifft2(laplacian_hat))
    return laplacian
```

### 2.2 Pseudo-Spectral Methods

**Dealiased convolution for nonlinear terms**:
```python
def dealiased_convolution(f, g, dx):
    """Compute f*g with 2/3 rule dealiasing"""
    N = len(f)
    M = 3 * N // 2  # Pad to 3/2

    # Zero padding
    f_pad = np.zeros(M, dtype=complex)
    g_pad = np.zeros(M, dtype=complex)
    f_pad[:N] = np.fft.fft(f)
    g_pad[:N] = np.fft.fft(g)

    # Multiply in Fourier space
    fg_hat = f_pad * g_pad

    # Truncate
    fg_hat = fg_hat[:N]

    # Transform back
    fg = np.real(np.fft.ifft(fg_hat))
    return fg
```

### 2.3 Accuracy

**Spectral accuracy**: Error decays exponentially for smooth functions

```python
# Example: sin(2πx) on [0,1]
def test_spectral_accuracy():
    errors = []
    for N in [16, 32, 64, 128, 256]:
        x = np.linspace(0, 1, N, endpoint=False)
        f = np.sin(2 * np.pi * x)

        # Spectral derivative
        df_spectral = spectral_derivative(f, 1/N, order=1)

        # Exact derivative
        df_exact = 2 * np.pi * np.cos(2 * np.pi * x)

        # Error
        error = np.max(np.abs(df_spectral - df_exact))
        errors.append(error)

    return errors  # Should decay exponentially
```

---

## 3. Finite Element Methods

### 3.1 Weak Formulation

**Example: Poisson equation** `-∇²u = f`

Multiply by test function φ and integrate:

```latex
∫∇u·∇φ dΩ = ∫fφ dΩ
```

### 3.2 Linear Basis Functions

**1D Hat functions**:
```python
def hat_function(x, i, nodes):
    """Hat function φ_i(x)"""
    xi = nodes[i]

    if x < nodes[i-1] or x > nodes[i+1]:
        return 0.0
    elif x < xi:
        return (x - nodes[i-1]) / (xi - nodes[i-1])
    else:
        return (nodes[i+1] - x) / (nodes[i+1] - xi)
```

### 3.3 Element Assembly

**Stiffness matrix**:
```python
def assemble_stiffness_1d(nodes):
    """Assemble stiffness matrix K_ij = ∫φ_i'φ_j' dx"""
    N = len(nodes)
    K = np.zeros((N, N))

    for i in range(N-1):
        h = nodes[i+1] - nodes[i]
        K[i, i] += 1/h
        K[i, i+1] -= 1/h
        K[i+1, i] -= 1/h
        K[i+1, i+1] += 1/h

    return K
```

**Mass matrix**:
```python
def assemble_mass_1d(nodes):
    """Assemble mass matrix M_ij = ∫φ_iφ_j dx"""
    N = len(nodes)
    M = np.zeros((N, N))

    for i in range(N-1):
        h = nodes[i+1] - nodes[i]
        M[i, i] += h/3
        M[i, i+1] += h/6
        M[i+1, i] += h/6
        M[i+1, i+1] += h/3

    return M
```

### 3.4 Time-Dependent Problems

**Method of lines**:
```python
def heat_equation_fem(u0, nodes, dt, T, kappa):
    """Solve heat equation using FEM in space, finite difference in time"""
    M = assemble_mass_1d(nodes)
    K = assemble_stiffness_1d(nodes)

    # Backward Euler: (M + dt*kappa*K)u_new = M*u_old
    A = M + dt * kappa * K

    u = u0.copy()
    t = 0.0

    while t < T:
        b = M @ u
        u = np.linalg.solve(A, b)
        t += dt

    return u
```

---

## 4. Stochastic Integration

### 4.1 Euler-Maruyama Method

**Strong order 0.5, Weak order 1.0**

```python
def euler_maruyama(x0, drift, diffusion, dt, T):
    """
    Integrate SDE: dX = μ(X)dt + σ(X)dW

    Args:
        x0: Initial condition
        drift: μ(x) function
        diffusion: σ(x) function
        dt: Time step
        T: Final time

    Returns:
        X: Trajectory
        t: Time points
    """
    Nt = int(T / dt)
    X = np.zeros(Nt + 1)
    t = np.zeros(Nt + 1)

    X[0] = x0
    t[0] = 0.0

    for n in range(Nt):
        # Wiener increment
        dW = np.random.randn() * np.sqrt(dt)

        # Update
        mu = drift(X[n])
        sigma = diffusion(X[n])

        X[n+1] = X[n] + mu * dt + sigma * dW
        t[n+1] = (n + 1) * dt

    return X, t
```

### 4.2 Milstein Method

**Strong order 1.0**

```python
def milstein(x0, drift, diffusion, ddiffusion, dt, T):
    """
    Integrate SDE with Milstein scheme (requires dσ/dx)

    Args:
        ddiffusion: ∂σ/∂x function
    """
    Nt = int(T / dt)
    X = np.zeros(Nt + 1)
    t = np.zeros(Nt + 1)

    X[0] = x0
    t[0] = 0.0

    for n in range(Nt):
        dW = np.random.randn() * np.sqrt(dt)

        mu = drift(X[n])
        sigma = diffusion(X[n])
        dsigma = ddiffusion(X[n])

        # Milstein update
        X[n+1] = (X[n] + mu * dt + sigma * dW +
                  0.5 * sigma * dsigma * (dW**2 - dt))
        t[n+1] = (n + 1) * dt

    return X, t
```

### 4.3 Itô vs Stratonovich

**Conversion**:
```python
def ito_to_stratonovich(drift_ito, diffusion):
    """Convert Itô SDE to Stratonovich"""
    def drift_strat(x):
        # Compute dσ/dx
        eps = 1e-6
        dsigma = (diffusion(x + eps) - diffusion(x)) / eps
        return drift_ito(x) - 0.5 * diffusion(x) * dsigma

    return drift_strat, diffusion
```

### 4.4 Weak Convergence

**Weak order**: Accuracy of expectations

```python
def weak_convergence_test(scheme, x0, T, n_trajectories=10000):
    """Test weak convergence of SDE solver"""
    dts = [0.1, 0.05, 0.025, 0.0125]
    errors = []

    for dt in dts:
        # Run many trajectories
        expectations = []
        for _ in range(n_trajectories):
            X, _ = scheme(x0, dt, T)
            expectations.append(X[-1])

        E_X = np.mean(expectations)
        errors.append(abs(E_X - E_exact))

    # Estimate order
    orders = np.log(errors[:-1] / errors[1:]) / np.log(2)
    return orders
```

---

## 5. Adaptive Methods

### 5.1 Adaptive Time Stepping

**Error control**:
```python
def adaptive_rk4(rhs, y0, t0, T, tol=1e-6):
    """
    Runge-Kutta-Fehlberg with adaptive time stepping
    """
    y = y0.copy()
    t = t0

    while t < T:
        # Try step
        dt = min(0.1, T - t)

        # RK4 (4th order)
        k1 = rhs(t, y)
        k2 = rhs(t + dt/2, y + dt*k1/2)
        k3 = rhs(t + dt/2, y + dt*k2/2)
        k4 = rhs(t + dt, y + dt*k3)

        y4 = y + dt * (k1 + 2*k2 + 2*k3 + k4) / 6

        # RK5 (5th order) for error estimation
        # ... (not shown)

        # Error estimate
        error = np.linalg.norm(y5 - y4)

        # Adjust time step
        if error < tol:
            y = y4  # Accept
            t += dt
            dt *= 1.2  # Increase
        else:
            dt *= 0.5  # Decrease and retry

    return y
```

### 5.2 Adaptive Mesh Refinement

**Error indicators**:
```python
def error_indicator(u):
    """Compute local error indicator"""
    # Gradient-based indicator
    grad_u = np.gradient(u)
    error = np.abs(np.gradient(grad_u))
    return error

def adapt_mesh(x, u, threshold):
    """Refine mesh where error is large"""
    error = error_indicator(u)

    # Find cells needing refinement
    refine_mask = error > threshold * np.max(error)

    # New mesh points
    x_new = []
    for i in range(len(x) - 1):
        x_new.append(x[i])
        if refine_mask[i]:
            x_new.append(0.5 * (x[i] + x[i+1]))
    x_new.append(x[-1])

    return np.array(x_new)
```

---

## 6. Parallel Computing

### 6.1 Domain Decomposition

**1D decomposition**:
```python
def decompose_1d(N, n_procs):
    """Decompose 1D domain into subdomains"""
    sizes = N // n_procs * np.ones(n_procs, dtype=int)
    sizes[:N % n_procs] += 1

    offsets = np.cumsum([0] + sizes.tolist())

    domains = []
    for i in range(n_procs):
        start, end = offsets[i], offsets[i+1]
        domains.append(slice(start, end))

    return domains
```

### 6.2 Parallel Finite Difference

```python
from mpi4py import MPI

def parallel_laplacian(u, dx):
    """Compute Laplacian in parallel"""
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Domain decomposition
    local_u = u[rank::size]

    # Exchange boundaries
    if rank > 0:
        left_neighbor = comm.sendrecv(local_u[0], dest=rank-1)
    if rank < size - 1:
        right_neighbor = comm.sendrecv(local_u[-1], dest=rank+1)

    # Compute Laplacian with ghost cells
    # ... (implementation)

    return local_laplacian
```

### 6.3 Parallel Spectral Methods

**FFTW-based**:
```python
import pyfftw

def parallel_fft(f):
    """Parallel FFT using pyFFTW"""
    # Align arrays for FFTW
    fft_input = pyfftw.empty_aligned(f.shape, dtype='complex128')
    fft_output = pyfftw.empty_aligned(f.shape, dtype='complex128')

    # Create FFT object
    fft_object = pyfftw.FFTW(fft_input, fft_output)

    # Compute FFT
    fft_input[:] = f
    fft_object()

    return fft_output
```

---

## Summary

This document covers:

1. **Finite difference methods**: Up to 2nd order accuracy
2. **Spectral methods**: Exponential accuracy for smooth solutions
3. **Finite element methods**: Flexible for complex geometries
4. **Stochastic integration**: Euler-Maruyama and Milstein schemes
5. **Adaptive methods**: Error control and mesh refinement
6. **Parallel computing**: Domain decomposition and parallel FFT

Each method is chosen based on:
- Problem type (elliptic, parabolic, hyperbolic, stochastic)
- Required accuracy
- Computational resources
- Solution smoothness

For POLLN analysis:
- **Fokker-Planck**: Crank-Nicolson finite difference
- **Information fluid**: Projection method with spectral Laplacian
- **Reaction-diffusion**: Spectral method for pattern formation
- **HJB**: Value iteration with adaptive meshing
- **SDEs**: Milstein scheme for strong convergence
