#!/usr/bin/env python3
"""
AMUNDSON–BLACKROAD FIELD CODEX — Phase VII Implementation
=========================================================
Variational principles (BR-8), GKSL open-system dynamics (BR-9),
energy–entropy balance (BR-10), and anisotropic learning tensor (AM-4),
with verification protocols P5–P7 and Unity WebSocket stub.

Author: BlackRoad Inc. / Alexa "Cecilia" Amundson
Date: 2025-11-06
Version: 1.0.0
Repo: blackboxprogramming/blackroad-prism-console
"""

import json
import socket
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import eigvalsh

# ---------- Compatibility layer (imports from Phase VI if present) ----------
try:  # pragma: no cover - optional dependency
    from codex_phase_06 import PhysicalConstants as _PC, UnitChecker as _UC

    CONST = _PC()
    UnitChecker = _UC
except Exception:  # pragma: no cover - safe fallback for standalone use

    @dataclass
    class PhysicalConstants:
        k_B: float = 1.380649e-23
        hbar: float = 1.054571817e-34
        c: float = 2.99792458e8

        @staticmethod
        def landauer_bound(T: float, N_bits: int = 1) -> float:
            return PhysicalConstants.k_B * T * np.log(2.0) * N_bits

    CONST = PhysicalConstants()

    class UnitChecker:  # pragma: no cover - trivial fallback implementation
        @staticmethod
        def check_continuity(A_units: str, J_units: str, t_units: str, x_units: str) -> bool:
            return True

        @staticmethod
        def check_diffusion(field_units: str, D_units: str, t_units: str) -> bool:
            return True

        @staticmethod
        def landauer_bound(T: float, N_bits: int = 1) -> float:
            return PhysicalConstants.landauer_bound(T, N_bits)

@dataclass
class LagrangianConfig:
    m_a: float = 1.0  # "mass" for a
    I_theta: float = 1.0  # inertia for theta
    gamma_a: float = 0.1  # dissipation on a-dot [kg/s equivalent]
    gamma_theta: float = 0.1  # dissipation on theta-dot
    k_a: float = 1.0  # spiral potential stiffness in a
    k_theta: float = 0.0  # periodic potential weight in theta
    rho_weight: float = 1.0  # trust potential weight


class VariationalSystem:
    """Minimal 2-DOF (a, theta) system with trust potential rho(t)."""

    def __init__(self, cfg: LagrangianConfig):
        self.cfg = cfg

    def V(self, a: float, theta: float, rho: float) -> float:
        # Spiral potential ~ 1/2 k_a a^2 plus optional periodic coupling in theta
        return 0.5*self.cfg.k_a*a*a + self.cfg.k_theta*(1-np.cos(theta)) + self.cfg.rho_weight*0.5*rho*rho

    def EL_rhs(self, t: float, y: np.ndarray, rho_fun: Callable[[float], float]) -> np.ndarray:
        a, a_dot, theta, theta_dot = y
        rho = rho_fun(t)
        dV_da = self.cfg.k_a * a
        dV_dtheta = self.cfg.k_theta * np.sin(theta)
        a_ddot = -(dV_da + self.cfg.gamma_a * a_dot) / self.cfg.m_a
        theta_ddot = -(dV_dtheta + self.cfg.gamma_theta * theta_dot) / self.cfg.I_theta
        return np.array([a_dot, a_ddot, theta_dot, theta_ddot], dtype=float)

    def leapfrog(self, y0: np.ndarray, t: np.ndarray, rho_fun: Callable[[float], float]) -> np.ndarray:
        """Symplectic leapfrog/velocity-Verlet integration (fixed dt)."""

        dt = t[1] - t[0]
        y = np.zeros((len(t), 4), dtype=float)
        y[0] = y0
        a, v, theta, omega = y0
        acc_state = self.EL_rhs(t[0], y0, rho_fun)
        v += 0.5 * dt * acc_state[1]
        omega += 0.5 * dt * acc_state[3]

        for i in range(1, len(t)):
            a += dt * v
            theta += dt * omega
            state = np.array([a, v, theta, omega], dtype=float)
            acc_state = self.EL_rhs(t[i], state, rho_fun)
            v += dt * acc_state[1]
            omega += dt * acc_state[3]
            y[i] = np.array(
                [a, v - 0.5 * dt * acc_state[1], theta, omega - 0.5 * dt * acc_state[3]],
                dtype=float,
            )
        return y

    @staticmethod
    def energy(cfg: LagrangianConfig, y: np.ndarray, rho_fun: Callable[[float], float], t: np.ndarray) -> np.ndarray:
        a, a_dot, th, th_dot = y.T
        rho = np.vectorize(rho_fun)(t)
        T = 0.5*cfg.m_a*a_dot*a_dot + 0.5*cfg.I_theta*th_dot*th_dot
        V = 0.5*cfg.k_a*a*a + cfg.k_theta*(1-np.cos(th)) + 0.5*cfg.rho_weight*rho*rho
        return T+V

# ============================== Section 3: GKSL Dynamics (BR-9) ==============================


def ensure_hermitian(matrix: np.ndarray) -> np.ndarray:
    return 0.5 * (matrix + matrix.conj().T)


class GKSL:
    def __init__(self, H: np.ndarray, L_ops: Tuple[np.ndarray, ...]):
        self.H = ensure_hermitian(H)
        self.L_ops = tuple(L_ops)

    @staticmethod
    def _d_rho(
        H: np.ndarray, L_ops: Tuple[np.ndarray, ...], rho: np.ndarray, hbar: float
    ) -> np.ndarray:
        commutator = H @ rho - rho @ H
        derivative = -1j / hbar * commutator
        for L in L_ops:
            LdL = L.conj().T @ L
            derivative += L @ rho @ L.conj().T - 0.5 * (LdL @ rho + rho @ LdL)
        return derivative

    def step_rk4(self, rho: np.ndarray, dt: float, hbar: float) -> np.ndarray:
        k1 = self._d_rho(self.H, self.L_ops, rho, hbar)
        k2 = self._d_rho(self.H, self.L_ops, rho + 0.5 * dt * k1, hbar)
        k3 = self._d_rho(self.H, self.L_ops, rho + 0.5 * dt * k2, hbar)
        k4 = self._d_rho(self.H, self.L_ops, rho + dt * k3, hbar)
        rho_next = rho + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        rho_next = ensure_hermitian(rho_next)
        vals, vecs = np.linalg.eigh(rho_next)
        vals = np.clip(vals.real, 0.0, None)
        rho_next = vecs @ np.diag(vals) @ vecs.conj().T
        trace = np.trace(rho_next).real
        if trace > 0:
            rho_next /= trace
        return rho_next


# ============================== Section 4: AM-4 Tensor ==============================


class AnisotropicLearningTensor:
    def __init__(self, Sigma: np.ndarray, Omega: np.ndarray):
        self.Sigma = np.array(Sigma, dtype=float)
        self.Omega = np.array(Omega, dtype=float)

    def U(self, tau: float) -> np.ndarray:
        generator = self.Sigma + 1j * self.Omega
        vals, vecs = np.linalg.eig(generator)
        return vecs @ np.diag(np.exp(vals * tau)) @ np.linalg.inv(vecs)

    def evolve(
        self,
        Psi0: np.ndarray,
        tau: np.ndarray,
        correction: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    ) -> np.ndarray:
        Psi = np.zeros((len(tau), len(Psi0)), dtype=complex)
        Psi[0] = Psi0
        for idx in range(1, len(tau)):
            dt = tau[idx] - tau[idx - 1]
            U_dt = self.U(dt)
            state = U_dt @ Psi[idx - 1]
            if correction is not None:
                state = state + dt * correction(Psi[idx - 1])
            Psi[idx] = state
        return Psi


# ============================== Section 5: Energy–Entropy Balance (BR-10) ==============================


def von_neumann_entropy(rho: np.ndarray) -> float:
    vals = np.clip(eigvalsh(ensure_hermitian(rho)), 1e-16, 1.0)
    return float(-np.sum(vals * np.log(vals)))


@dataclass
class EnergyEntropyReport:
    E: np.ndarray
    S: np.ndarray
    dS_nonneg: bool
    landauer_ok: bool

def first_law_validator(E_dot: np.ndarray, S_dot: np.ndarray, T: float, dt: float,
                        decisions: int) -> EnergyEntropyReport:
    E = np.cumsum(E_dot)*dt
    S = np.cumsum(S_dot)*dt
    dS_nonneg = (S[-1] - S[0]) >= -1e-10
    landauer_ok = (E[-1] >= CONST.landauer_bound(T, decisions) - 1e-12)
    return EnergyEntropyReport(E=E, S=S, dS_nonneg=dS_nonneg, landauer_ok=landauer_ok)

# ============================== Section 6: Verification Suite (P5–P7) ==============================


class VerificationVII:
    @staticmethod
    def P5_variational(T_end: float = 10.0, N: int = 2000) -> Dict[str, np.ndarray]:
        cfg = LagrangianConfig(m_a=1.0, I_theta=1.0, gamma_a=0.05, gamma_theta=0.05, k_a=0.4, k_theta=0.2)
        system = VariationalSystem(cfg)
        t = np.linspace(0.0, T_end, N)
        rho_fun = lambda tt: 0.2 * np.sin(0.5 * tt)
        y0 = np.array([0.2, 0.0, 0.0, 0.0], dtype=float)
        trajectory = system.leapfrog(y0, t, rho_fun)
        energy = VariationalSystem.energy(cfg, trajectory, rho_fun, t)
        energy_drift = float(energy[-1] - energy[0])
        return {"t": t, "traj": trajectory, "energy": energy, "energy_drift": energy_drift}

    @staticmethod
    def P6_gksl(T_end: float = 2.0, N: int = 400, gamma: float = 0.4) -> Dict[str, np.ndarray]:
        H = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)
        L = np.sqrt(gamma) * np.array([[0.0, 1.0], [0.0, 0.0]], dtype=complex)
        gksl = GKSL(H, (L,))
        t = np.linspace(0.0, T_end, N)
        dt = t[1] - t[0]
        rho = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)
        entropy_vals = []
        trace_err = []
        purity = []
        states = np.zeros((N, 2, 2), dtype=complex)
        for idx in range(N):
            states[idx] = rho
            entropy_vals.append(von_neumann_entropy(rho))
            trace_err.append(abs(np.trace(rho).real - 1.0))
            purity.append(np.trace(rho @ rho).real)
            if idx < N - 1:
                rho = gksl.step_rk4(rho, dt, CONST.hbar)
        entropy_arr = np.array(entropy_vals, dtype=float)
        if entropy_arr.size > 1:
            diffs = np.diff(entropy_arr)
            min_diff = float(np.min(diffs))
            assert min_diff >= -1e-3, f"Entropy not monotone (tolerance), min ΔS={min_diff:.3e}"
        return {
            "t": t,
            "states": states,
            "entropy": np.array(entropy_vals),
            "trace_error": np.array(trace_err),
            "purity": np.array(purity),
        }

    @staticmethod
    def P7_thermo(
        T_end: float = 1.0,
        N: int = 200,
        T_kelvin: float = 300.0,
        decisions: int = 100,
    ) -> Dict[str, np.ndarray]:
        p6 = VerificationVII.P6_gksl(T_end=T_end, N=N, gamma=0.5)
        entropy = p6["entropy"]
        t = p6["t"]
        dt = t[1] - t[0]
        energy_rate = np.full_like(t, 1e-21)
        entropy_rate = np.gradient(entropy, dt)
        report = first_law_validator(energy_rate, entropy_rate, T_kelvin, dt, decisions)
        return {
            "t": t,
            "E": report.E,
            "S": report.S,
            "dS_nonneg": report.dS_nonneg,
            "landauer_ok": report.landauer_ok,
        }


# ============================== Section 7: Visualization ==============================


class VizVII:
    @staticmethod
    def plot_P5(res: Dict[str, np.ndarray], save_path: Optional[str] = None) -> None:
        t = res["t"]
        traj = res["traj"]
        energy = res["energy"]
        fig = plt.figure(figsize=(10, 6))
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.plot(t, traj[:, 0], label="a")
        ax1.plot(t, traj[:, 2], label="theta")
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("States a, theta")
        ax1.legend()
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.plot(t, energy)
        ax2.set_xlabel("Time [s]")
        ax2.set_ylabel("Energy [J]")
        plt.tight_layout()
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def plot_P6(res: Dict[str, np.ndarray], save_path: Optional[str] = None) -> None:
        t = res["t"]
        entropy = res["entropy"]
        trace_err = res["trace_error"]
        purity = res["purity"]
        fig = plt.figure(figsize=(10, 6))
        ax1 = fig.add_subplot(3, 1, 1)
        ax1.plot(t, entropy)
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("Von Neumann S")
        ax2 = fig.add_subplot(3, 1, 2)
        ax2.plot(t, trace_err)
        ax2.set_xlabel("Time [s]")
        ax2.set_ylabel("|Tr(ρ)-1|")
        ax3 = fig.add_subplot(3, 1, 3)
        ax3.plot(t, purity)
        ax3.set_xlabel("Time [s]")
        ax3.set_ylabel("Purity Tr(ρ²)")
        plt.tight_layout()
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def plot_P7(res: Dict[str, np.ndarray], save_path: Optional[str] = None) -> None:
        t = res["t"]
        energy = res["E"]
        entropy = res["S"]
        fig = plt.figure(figsize=(10, 6))
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.plot(t, energy)
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("Energy cum. [J]")
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.plot(t, entropy)
        ax2.set_xlabel("Time [s]")
        ax2.set_ylabel("Entropy cum.")
        plt.tight_layout()
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)


# ============================== Section 8: Unity Bridge Stub ==============================


class UnityBridge:
    """Very lightweight UDP sender targeting a Unity listener."""

    def __init__(self, host: str = "127.0.0.1", port: int = 44444):
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, payload: Dict[str, object]) -> None:
        message = json.dumps({"topic": "phase_vii", "t": time.time(), "payload": payload})
        self.sock.sendto(message.encode("utf-8"), self.addr)

    def close(self) -> None:
        self.sock.close()


# ============================== CLI ==============================


def run_full_vii() -> Dict[str, Dict[str, np.ndarray]]:
    print("=== Phase VII: Running P5–P7 ===")
    p5 = VerificationVII.P5_variational()
    p6 = VerificationVII.P6_gksl()
    p7 = VerificationVII.P7_thermo()
    VizVII.plot_P5(p5, save_path="figures/P5_variational.png")
    VizVII.plot_P6(p6, save_path="figures/P6_gksl.png")
    VizVII.plot_P7(p7, save_path="figures/P7_thermo.png")
    print("P5 energy drift:", p5["energy_drift"])
    print("P6 max trace error:", float(np.max(p6["trace_error"])))
    print("P7 dS_nonneg:", p7["dS_nonneg"], "landauer_ok:", p7["landauer_ok"])
    return {"P5": p5, "P6": p6, "P7": p7}


def _main() -> None:
    import sys

    commands = {"p5", "p6", "p7", "full"}
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd not in commands:
            print("Usage: python codex_phase_07.py [p5|p6|p7|full]")
            return
        if cmd == "full":
            run_full_vii()
            return

        mapping = {
            "p5": (VerificationVII.P5_variational, VizVII.plot_P5),
            "p6": (VerificationVII.P6_gksl, VizVII.plot_P6),
            "p7": (VerificationVII.P7_thermo, VizVII.plot_P7),
        }
        factory, plotter = mapping[cmd]
        result = factory()
        plotter(result)
    else:
        run_full_vii()


if __name__ == "__main__":
    _main()
