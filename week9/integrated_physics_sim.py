"""
Integrated Physics Simulator (Week 9)
통합 고전 역학 시뮬레이터

이 프로그램은 Week 9에서 배운 모든 물리 시뮬레이션을 하나로 통합한 도구입니다.
1. 수치 적분 비교 (Euler vs RK4)
2. 행성 운동 (케플러 법칙)
3. 혼돈 시스템 (이중 진자)
4. 역학 정식화 비교 (Newton, Lagrange, Hamilton)
5. 3체 문제 (Figure-8, 안정 궤도)

사용법:
python integrated_physics_sim.py --lab [1-5]
또는 실행 후 메뉴에서 선택
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import argparse
import time

# ============================================================================
# 공통 유틸리티 및 엔진
# ============================================================================

class PhysicsEngine:
    @staticmethod
    def euler_step(f, y, t, dt):
        """오일러 방법 (1차)"""
        return y + dt * f(y, t)

    @staticmethod
    def rk4_step(f, y, t, dt):
        """Runge-Kutta 4차 방법 (4차)"""
        k1 = f(y, t)
        k2 = f(y + 0.5*dt*k1, t + 0.5*dt)
        k3 = f(y + 0.5*dt*k2, t + 0.5*dt)
        k4 = f(y + dt*k3, t + dt)
        return y + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)

    @staticmethod
    def simulate(f, y0, t_max, dt, method='rk4'):
        """범용 시뮬레이션 루프"""
        step_func = PhysicsEngine.rk4_step if method == 'rk4' else PhysicsEngine.euler_step
        n_steps = int(t_max / dt)
        t_array = np.linspace(0, t_max, n_steps)
        history = np.zeros((n_steps, len(y0)))
        
        y = np.array(y0, dtype=float)
        for i in range(n_steps):
            history[i] = y
            y = step_func(f, y, t_array[i], dt)
            
        return t_array, history

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# ============================================================================
# Lab 1: Numerical Integration (Euler vs RK4)
# ============================================================================

def lab_integration():
    print("\n[Lab 1] Numerical Integration: Euler vs RK4")
    output_dir = 'outputs/integrated/lab1'
    ensure_dir(output_dir)
    
    omega = 2 * np.pi
    def sho(y, t):
        x, v = y
        return np.array([v, -omega**2 * x])

    y0 = [1.0, 0.0]
    t_max, dt = 10.0, 0.1
    
    t_euler, h_euler = PhysicsEngine.simulate(sho, y0, t_max, dt, 'euler')
    t_rk4, h_rk4 = PhysicsEngine.simulate(sho, y0, t_max, dt, 'rk4')
    
    # Exact solution
    t_exact = np.linspace(0, t_max, 1000)
    x_exact = np.cos(omega * t_exact)
    
    # Energy
    E0 = 0.5 * omega**2
    E_euler = 0.5 * (h_euler[:, 1]**2 + (omega * h_euler[:, 0])**2)
    E_rk4 = 0.5 * (h_rk4[:, 1]**2 + (omega * h_rk4[:, 0])**2)

    plt.figure(figsize=(14, 6))
    plt.subplot(121)
    plt.plot(t_exact, x_exact, 'k-', alpha=0.3, label='Exact')
    plt.plot(t_euler, h_euler[:, 0], 'r--', label='Euler')
    plt.plot(t_rk4, h_rk4[:, 0], 'b-', label='RK4')
    plt.title('Position Comparison')
    plt.legend()
    
    plt.subplot(122)
    plt.plot(t_euler, (E_euler - E0)/E0 * 100, 'r--', label='Euler Error')
    plt.plot(t_rk4, (E_rk4 - E0)/E0 * 100, 'b-', label='RK4 Error')
    plt.title('Energy Error (%)')
    plt.legend()
    
    plt.savefig(f"{output_dir}/integration_comparison.png")
    print(f"Results saved to {output_dir}")

# ============================================================================
# Lab 2: Planetary Motion (Kepler's Laws)
# ============================================================================

def lab_planetary():
    print("\n[Lab 2] Planetary Motion: Kepler's Laws")
    output_dir = 'outputs/integrated/lab2'
    ensure_dir(output_dir)
    
    G = 4 * np.pi**2
    M_sun = 1.0
    
    def gravity(y, t):
        x, y_pos, vx, vy = y
        r = np.sqrt(x**2 + y_pos**2)
        a = -G * M_sun / r**3
        return np.array([vx, vy, a*x, a*y_pos])

    # Earth: a=1.0, e=0.0167
    a, e = 1.0, 0.0167
    r0 = a * (1 - e)
    v0 = np.sqrt(G * M_sun * (1 + e) / (a * (1 - e)))
    
    t, h = PhysicsEngine.simulate(gravity, [r0, 0, 0, v0], 2.0, 0.001)
    
    plt.figure(figsize=(8, 8))
    plt.plot(h[:, 0], h[:, 1], 'b-', label='Earth Orbit')
    plt.plot(0, 0, 'yo', markersize=15, label='Sun')
    plt.axis('equal')
    plt.title('Planetary Motion (Earth)')
    plt.legend()
    plt.savefig(f"{output_dir}/earth_orbit.png")
    print(f"Results saved to {output_dir}")

# ============================================================================
# Lab 3: Chaotic Systems (Double Pendulum)
# ============================================================================

def lab_chaos():
    print("\n[Lab 3] Chaotic Systems: Double Pendulum")
    output_dir = 'outputs/integrated/lab3'
    ensure_dir(output_dir)
    
    g, L1, L2, m1, m2 = 9.81, 1.0, 1.0, 1.0, 1.0
    
    def derivs(y, t):
        th1, w1, th2, w2 = y
        delta = th2 - th1
        den1 = (m1+m2)*L1 - m2*L1*np.cos(delta)**2
        den2 = (L2/L1)*den1
        dw1 = (m2*L1*w1**2*np.sin(delta)*np.cos(delta) + m2*g*np.sin(th2)*np.cos(delta) + 
               m2*L2*w2**2*np.sin(delta) - (m1+m2)*g*np.sin(th1)) / den1
        dw2 = (-m2*L2*w2**2*np.sin(delta)*np.cos(delta) + (m1+m2)*(g*np.sin(th1)*np.cos(delta) - 
               L1*w1**2*np.sin(delta) - g*np.sin(th2))) / den2
        return np.array([w1, dw1, w2, dw2])

    t, h1 = PhysicsEngine.simulate(derivs, [np.pi/2, 0, np.pi/2, 0], 20.0, 0.01)
    t, h2 = PhysicsEngine.simulate(derivs, [np.pi/2, 0, np.pi/2+0.0001, 0], 20.0, 0.01)
    
    x2_1 = L1*np.sin(h1[:, 0]) + L2*np.sin(h1[:, 2])
    y2_1 = -L1*np.cos(h1[:, 0]) - L2*np.cos(h1[:, 2])
    x2_2 = L1*np.sin(h2[:, 0]) + L2*np.sin(h2[:, 2])
    y2_2 = -L1*np.cos(h2[:, 0]) - L2*np.cos(h2[:, 2])
    
    plt.figure(figsize=(10, 8))
    plt.plot(x2_1, y2_1, 'b-', alpha=0.6, label='Pendulum 1')
    plt.plot(x2_2, y2_2, 'r-', alpha=0.6, label='Pendulum 2 (diff=0.0001)')
    plt.title('Double Pendulum: Chaos')
    plt.legend()
    plt.savefig(f"{output_dir}/chaos_divergence.png")
    print(f"Results saved to {output_dir}")

# ============================================================================
# Lab 4: Mechanics Formalisms (Newton/Lagrange/Hamilton)
# ============================================================================

def lab_mechanics():
    print("\n[Lab 4] Mechanics Formalisms: Newton/Lagrange/Hamilton")
    output_dir = 'outputs/integrated/lab4'
    ensure_dir(output_dir)
    
    g, L, m = 9.81, 1.0, 1.0
    
    def newton_lagrange(y, t):
        th, w = y
        return np.array([w, -(g/L)*np.sin(th)])
    
    def hamilton(y, t):
        th, p = y
        return np.array([p/(m*L**2), -m*g*L*np.sin(th)])

    th0 = np.pi/3
    t, h_nl = PhysicsEngine.simulate(newton_lagrange, [th0, 0], 10.0, 0.01)
    t, h_h = PhysicsEngine.simulate(hamilton, [th0, 0], 10.0, 0.01)
    
    plt.figure(figsize=(10, 5))
    plt.plot(t, np.degrees(h_nl[:, 0]), 'b-', label='Newton/Lagrange')
    plt.plot(t, np.degrees(h_h[:, 0]), 'r--', label='Hamilton')
    plt.title('Formulation Comparison')
    plt.legend()
    plt.savefig(f"{output_dir}/formulation_comparison.png")
    print(f"Results saved to {output_dir}")

# ============================================================================
# Lab 5: Three-Body Problem (Figure-8)
# ============================================================================

def lab_three_body():
    print("\n[Lab 5] Three-Body Problem: Figure-8 Orbit")
    output_dir = 'outputs/integrated/lab5'
    ensure_dir(output_dir)
    
    m1 = m2 = m3 = 1.0
    G = 1.0
    
    def three_body(y, t):
        r1, v1 = y[0:2], y[2:4]
        r2, v2 = y[4:6], y[6:8]
        r3, v3 = y[8:10], y[10:12]
        
        r12, r13, r23 = r2-r1, r3-r1, r3-r2
        d12, d13, d23 = np.linalg.norm(r12), np.linalg.norm(r13), np.linalg.norm(r23)
        
        a1 = G*m2/d12**3*r12 + G*m3/d13**3*r13
        a2 = -G*m1/d12**3*r12 + G*m3/d23**3*r23
        a3 = -G*m1/d13**3*r13 - G*m2/d23**3*r23
        
        return np.concatenate([v1, a1, v2, a2, v3, a3])

    # Figure-8 IC
    x1, y1 = -0.97000436, 0.24308753
    vx1, vy1 = 0.466203685, 0.43236573
    y0 = [x1, y1, vx1, vy1, -x1, -y1, vx1, vy1, 0, 0, -2*vx1, -2*vy1]
    
    t, h = PhysicsEngine.simulate(three_body, y0, 6.3259, 0.001)
    
    plt.figure(figsize=(8, 8))
    plt.plot(h[:, 0], h[:, 1], 'r-', label='Body 1')
    plt.plot(h[:, 4], h[:, 5], 'g-', label='Body 2')
    plt.plot(h[:, 8], h[:, 9], 'b-', label='Body 3')
    plt.axis('equal')
    plt.title('Three-Body: Figure-8 Orbit')
    plt.legend()
    plt.savefig(f"{output_dir}/figure8.png")
    print(f"Results saved to {output_dir}")

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Integrated Physics Simulator")
    parser.add_argument("--lab", type=int, choices=[1, 2, 3, 4, 5], help="Lab number to run")
    parser.add_argument("--all", action="store_true", help="Run all labs")
    args = parser.parse_args()

    labs = {
        1: lab_integration,
        2: lab_planetary,
        3: lab_chaos,
        4: lab_mechanics,
        5: lab_three_body
    }

    if args.all:
        for i in range(1, 6):
            labs[i]()
    elif args.lab:
        labs[args.lab]()
    else:
        print("\n" + "="*50)
        print("  WEEK 9: INTEGRATED PHYSICS SIMULATOR")
        print("="*50)
        print("  1. Numerical Integration (Euler vs RK4)")
        print("  2. Planetary Motion (Kepler's Laws)")
        print("  3. Chaotic Systems (Double Pendulum)")
        print("  4. Mechanics Formalisms (Newton/Lagrange/Hamilton)")
        print("  5. Three-Body Problem (Figure-8)")
        print("  6. Run ALL Labs")
        print("  0. Exit")
        print("-" * 50)
        
        try:
            choice = int(input("  Select a lab (0-6): "))
            if choice == 0:
                return
            elif choice == 6:
                for i in range(1, 6): labs[i]()
            elif choice in labs:
                labs[choice]()
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")

if __name__ == "__main__":
    main()
