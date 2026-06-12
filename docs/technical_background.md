# Technical Background

This project uses small molecules as controlled validation systems before
attempting larger ALD-inspired chemistry. The goal is to keep each numerical
step checkable: classical references, many-body Hamiltonians, qubit mappings and
variational solvers should agree on H2 before being trusted elsewhere.

## Born-Oppenheimer Approximation

Electronic-structure calculations usually separate slow nuclear motion from
fast electronic motion. For a fixed molecular geometry, the nuclei are treated
as stationary point charges and the electronic Schrodinger equation is solved.
The nuclear repulsion energy is then added to the electronic energy to obtain a
total molecular energy for that geometry.

## Hartree-Fock

Hartree-Fock approximates the electronic wavefunction by a single Slater
determinant. It captures antisymmetry exactly but treats electron correlation
only in a mean-field way. In this repository, PySCF Hartree-Fock provides the
molecular orbitals and a first total-energy reference.

## FCI

Full configuration interaction diagonalizes the electronic Hamiltonian in all
determinants available in a chosen finite orbital basis. For H2/STO-3G this is
small enough to be an exact reference within that basis. FCI still depends on
the chosen basis set; it is not the exact continuum molecular energy.

## CASCI

Complete active-space configuration interaction is an exact diagonalization
inside a selected active space while keeping the underlying molecular orbitals
fixed. CASCI is therefore different from full FCI: it omits determinants outside
the chosen active orbitals. When the active space is smaller than the full
orbital space, CASCI validates a reduced model rather than the complete
finite-basis molecule.

## Active Space

An active space selects a subset of electrons and orbitals for correlated
treatment. This reduces the size of the Hilbert space, but it changes the model
unless frozen-core and external-orbital energy shifts are handled carefully.
H2/STO-3G is small enough to use the full minimal space. LiH is treated more
cautiously and any reduced active-space result is labelled as exploratory.

For LiH/STO-3G, a reduced CASCI(2,2) model keeps two electrons in two active
spatial orbitals. PySCF provides an effective active-space one-electron
Hamiltonian and a core energy shift. The local active-space diagonalization must
add this core energy shift before comparing with PySCF CASCI total energies.
The difference between CASCI(2,2) and full FCI is the expected active-space
truncation error, not a Hamiltonian-construction error.

## Second Quantization

Second quantization represents electronic Hamiltonians with fermionic creation
and annihilation operators. A typical electronic Hamiltonian has one-body terms
for kinetic energy and nuclear attraction, plus two-body electron-repulsion
terms. Careful integral-index conventions matter: PySCF reports two-electron
integrals in chemist's notation.

## Occupation-Number Basis

The occupation-number basis encodes which spin-orbitals are occupied. A basis
state is a bitstring, with one bit per spin-orbital. This makes small dense
Hamiltonians easy to construct and inspect, but the dimension grows
exponentially.

## Fixed-Particle Sector

Physical molecular calculations conserve electron number. The local many-body
Hamiltonian is therefore built or restricted to the sector with exactly the
right number of electrons. For H2/STO-3G there are four spin-orbitals and two
electrons, so the sector dimension is C(4,2) = 6.

## Fermion-to-Qubit Mapping

Quantum algorithms require mapping fermionic operators to qubit operators.
Jordan-Wigner is the simplest mapping and preserves the fermionic algebra by
using strings of Pauli Z operators. The qubit Hamiltonian acts on the full qubit
Hilbert space, so validation must compare the physically relevant
fixed-particle sector or clearly state what spectrum is being compared.

## VQE

The variational quantum eigensolver prepares a parameterized trial state and
minimizes the expected energy. The pure-Python fallback in this repository works
directly with small dense matrices and is pedagogical. It is useful for testing
the pipeline on H2, but it is not a scalable backend.

## Why H2 First?

H2/STO-3G is small, reproducible and analytically understandable. It lets the
project validate Hartree-Fock, FCI, fixed-sector Hamiltonian construction,
local diagonalization, fallback VQE and Jordan-Wigner mapping before adding
larger molecules.

## Why This Is Not Yet a Realistic ALD Simulation

Real ALD chemistry involves surfaces, precursors, transition states, larger
active spaces, basis-set effects and environmental modelling. This repository is
currently a validation scaffold. H2 and cautious LiH tests establish numerical
trust in the workflow, but they do not yet represent production ALD chemistry.
