# Mathematical Framework

## 2.1 Spherical Harmonics

### Definition D1 (Spherical Harmonic)
The **spherical harmonic** of degree $l$ and order $m$ is:

$$Y_l^m(\theta, \phi) = N_{l,m} P_l^m(\cos\theta) e^{im\phi}$$

Where:
- $N_{l,m} = \sqrt{\frac{2l+1}{4\pi}\frac{(l-m)!}{(l+m)!}}$ is the normalization
- $P_l^m$ is the associated Legendre polynomial

### Definition D2 (Spherical Function Space)
The space of square-integrable functions on $S^2$:

$$L^2(S^2) = \{ f: S^2 \to \mathbb{R} : \int_{S^2} |f|^2 d\Omega < \infty \}$$

### Theorem T1 (Spherical Harmonic Basis)
$\{Y_l^m\}_{l=0}^{\infty, m=-l}^{l}$ forms an orthonormal basis for $L^2(S^2)$.

**Proof**:
1. Orthonormality: $\int Y_l^m \overline{Y_{l'}^{m'}} d\Omega = \delta_{ll'}\delta_{mm'}$ (standard result)
2. Completeness: Follows from Stone-Weierstrass on compact manifolds
3. Therefore, $\{Y_l^m\}$ is a basis. $\square$

## 2.2 Wigner D-Matrices

### Definition D3 (Wigner D-Matrix)
For angular momentum $l$, the **Wigner D-matrix** is a $(2l+1) \times (2l+1)$ matrix with entries:

$$D^l_{m,m'}(\alpha, \beta, \gamma) = e^{-im\alpha} d^l_{m,m'}(\beta) e^{-im'\gamma}$$

Where $d^l_{m,m'}(\beta)$ is the Wigner small d-matrix.

### Definition D4 (Wigner Small d-Matrix)
$$d^l_{m,m'}(\beta) = \sum_k \frac{(-1)^k \sqrt{(l+m)!(l-m)!(l+m')!(l-m')!}}{(l+m-k)!(l-m'-k)!k!(k+m'-m)!} \times \cos^{2l+m-m'-2k}(\beta/2) \sin^{m'-m+2k}(\beta/2)$$

### Theorem T2 (Rotation Transformation)
Under rotation $R(\alpha, \beta, \gamma)$ (Euler angles):

$$Y_l^m(R^{-1}\hat{r}) = \sum_{m'=-l}^{l} D^l_{m',m}(R) Y_l^{m'}(\hat{r})$$

**Proof**:
1. Spherical harmonics are eigenfunctions of angular momentum
2. Rotation operators act on angular momentum eigenstates
3. Wigner D-matrix encodes this action
4. Therefore, transformation follows. $\square$

## 2.3 Spherical Tensors

### Definition D5 (Spherical Tensor)
A **spherical tensor** of rank $l$ is a collection of $(2l+1)$ components $\{T_m^l\}_{m=-l}^{l}$ that transform under rotation as:

$$T_m^l \to \sum_{m'=-l}^{l} D^l_{m,m'}(R) T_{m'}^l$$

### Definition D6 (Spherical Tensor Product)
The tensor product of spherical tensors of rank $l_1$ and $l_2$:

$$(T^{l_1} \otimes U^{l_2})_m^l = \sum_{m_1, m_2} C_{l_1,m_1;l_2,m_2}^{l,m} T_{m_1}^{l_1} U_{m_2}^{l_2}$$

Where $C_{l_1,m_1;l_2,m_2}^{l,m}$ are Clebsch-Gordan coefficients.

### Theorem T3 (Clebsch-Gordan Selection Rules)
The tensor product $T^{l_1} \otimes U^{l_2}$ contains spherical tensors of rank $l$ where:

$$|l_1 - l_2| \leq l \leq l_1 + l_2$$

**Proof**: Follows from angular momentum addition in quantum mechanics. $\square$

## 2.4 Spherical Convolution

### Definition D7 (Spherical Convolution)
For spherical functions $f, g \in L^2(S^2)$:

$$(f * g)(\hat{r}) = \int_{SO(3)} f(R\hat{r}_0) g(R^{-1}\hat{r}) dR$$

Where $\hat{r}_0$ is the north pole.

### Theorem T4 (Convolution in Harmonic Space)
In the spherical harmonic basis:

$$\widehat{(f * g)}_l = \hat{f}_l \odot \hat{g}_l$$

Where $\odot$ denotes the matrix product in the $(2l+1)$-dimensional space.

**Proof**:
1. Express convolution in harmonic basis
2. Use Wigner D-matrix orthogonality
3. Result follows from harmonic product theorem. $\square$

### Definition D8 (Wigner-D Convolution Layer)
A **Wigner-D convolution** layer computes:

$$\text{Conv}(f)_l = \sum_{l'} W_{l,l'} \hat{f}_{l'}$$

Where $W_{l,l'}$ are learnable $(2l+1) \times (2l'+1)$ matrices.

## 2.5 Equivariance Properties

### Theorem T5 (Rotation Equivariance)
Wigner-D convolution layers are rotation-equivariant:

$$\text{Conv}(R \cdot f) = R \cdot \text{Conv}(f)$$

**Proof**:
1. Input transforms: $\hat{f}_l \to D^l(R) \hat{f}_l$
2. Convolution output: $W_{l,l'} D^{l'}(R) \hat{f}_{l'}$
3. If $W_{l,l'}$ is spherical tensor, transforms as $D^l(R) W_{l,l'}$
4. Therefore: $D^l(R) W_{l,l'} \hat{f}_{l'} = D^l(R) \cdot \text{Conv}(f)$
5. Equivariance holds. $\square$

### Theorem T6 (Bandwidth Conservation)
If input has bandwidth $L$ (non-zero only for $l \leq L$), output has bandwidth $\leq L$.

**Proof**:
1. Convolution at level $l$ only uses $\hat{f}_{l'}$ for $l' \leq l$
2. No new high-frequency components created
3. Therefore, bandwidth is conserved. $\square$

## 2.6 Nonlinearities

### Definition D9 (Spherical Nonlinearity)
A **spherical nonlinearity** acts on the norm of spherical tensor components:

$$\text{NormReLU}(T^l) = \text{ReLU}\left(\sqrt{\sum_m |T_m^l|^2}\right) \cdot \frac{T^l}{\|T^l\|}$$

### Theorem T7 (Nonlinearity Equivariance)
Norm-based nonlinearities preserve rotation equivariance.

**Proof**:
1. Norm $\|T^l\|$ is rotation-invariant (scalar)
2. Direction $T^l/\|T^l\|$ transforms correctly
3. Scalar multiplication preserves transformation
4. Therefore, equivariance maintained. $\square$

## 2.7 Computational Complexity

### Theorem T8 (Convolution Complexity)
Wigner-D convolution with bandwidth $L$ has complexity $O(L^3)$.

**Proof**:
1. Number of $l$ values: $L$
2. Matrix size at level $l$: $(2l+1) \times (2l+1)$
3. Sum of squares: $\sum_{l=0}^{L} (2l+1)^2 = O(L^3)$
4. Therefore, complexity is $O(L^3)$. $\square$

---

## Bibliography

```bibtex
@book{varshalovich1988quantum,
  title={Quantum Theory of Angular Momentum},
  author={Varshalovich, Dmitri A and Moskalev, Anatol N and Khersonskii, Valerii K},
  year={1988},
  publisher={World Scientific}
}

@article{wigner1959group,
  title={Group Theory and its Application to the Quantum Mechanics of Atomic Spectra},
  author={Wigner, Eugene P},
  journal={Pure and Applied Physics},
  year={1959}
}
```

---

*Part of the SuperInstance Mathematical Framework*
