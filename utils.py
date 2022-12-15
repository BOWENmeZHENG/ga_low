import numpy as np
import matplotlib.pyplot as plt


def load_flakes():
    f7 = np.loadtxt('flakes/f7.txt', dtype=float)
    f9 = np.loadtxt('flakes/f9.txt', dtype=float)
    f11 = np.loadtxt('flakes/f11.txt', dtype=float)
    f12 = np.loadtxt('flakes/f12.txt', dtype=float)
    f14 = np.loadtxt('flakes/f14.txt', dtype=float)
    f16 = np.loadtxt('flakes/f16.txt', dtype=float)
    f18 = np.loadtxt('flakes/f18.txt', dtype=float)
    f20 = np.loadtxt('flakes/f20.txt', dtype=float)
    p = np.array([0.00489, 0.0797, 0.1856, 0.1828, 0.101, 0.0336, 0.008113, 0.001589])  # log-normal probabilities of flakes
    p /= sum(p)
    return [f7, f9, f11, f12, f14, f16, f18, f20], p

def plot_3D(coors_flakes_all, coors_inclusions):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(projection='3d')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.scatter(coors_flakes_all[:, 0], coors_flakes_all[:, 1], coors_flakes_all[:, 2], s=1)
    ax.scatter(coors_inclusions[:, 0], coors_inclusions[:, 1], coors_inclusions[:, 2])
    plt.show()