import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Parámetros de la simulación
LAMBDA = 60 / 3600   # Tasa de llegada: 60 clientes por hora (clientes/segundo)
MU = 1 / 150         # Tasa de servicio: corresponde a un tiempo medio de 150 segundos
SIM_TIME = 8 * 3600  # Tiempo de simulación: 8 horas (en segundos)
NUM_SERVERS = 3      # Número de servidores

def customer_separate(env, queue_id, queues, total_times):
    arrive = env.now
    with queues[queue_id].request() as req:
        yield req
        yield env.timeout(random.expovariate(MU))
    total_time = env.now - arrive
    total_times.append(total_time)

def setup_separate_queues(env, num_queues):
    queues = [simpy.Resource(env, capacity=1) for _ in range(num_queues)]
    return queues

def arrive_separate(env, queues, total_times):
    while True:
        yield env.timeout(random.expovariate(LAMBDA))
        queue_id = random.randint(0, len(queues) - 1)
        env.process(customer_separate(env, queue_id, queues, total_times))

def customer_single(env, queue, total_times):
    arrive = env.now
    with queue.request() as req:
        yield req
        yield env.timeout(random.expovariate(MU))
    total_time = env.now - arrive
    total_times.append(total_time)

def setup_single_queue(env, num_servers):
    queue = simpy.Resource(env, capacity=num_servers)
    return queue

def arrive_single(env, queue, total_times):
    while True:
        yield env.timeout(random.expovariate(LAMBDA))
        env.process(customer_single(env, queue, total_times))

def run_simulation():
    env1 = simpy.Environment()
    queues = setup_separate_queues(env1, NUM_SERVERS)
    total_times_separate = []
    env1.process(arrive_separate(env1, queues, total_times_separate))
    env1.run(until=SIM_TIME)
    avg_time_separate = np.mean(total_times_separate) if total_times_separate else 0
    env2 = simpy.Environment()
    queue = setup_single_queue(env2, NUM_SERVERS)
    total_times_single = [] 
    env2.process(arrive_single(env2, queue, total_times_single))
    env2.run(until=SIM_TIME)
    avg_time_single = np.mean(total_times_single) if total_times_single else 0
    return avg_time_separate, avg_time_single, total_times_separate, total_times_single

def plot_results(total_times_separate, total_times_single):
    plt.figure(figsize=(10, 6))
    plt.hist(total_times_separate, bins=50, density=True, alpha=0.7,label='Tiempo Total (Colas Separadas)')
    plt.title('Distribución de Tiempos Totales (Colas Separadas)')
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Densidad')
    plt.legend()
    plt.savefig('separate_queues_times.png')
    plt.close()
    plt.figure(figsize=(10, 6))
    plt.hist(total_times_single, bins=50, density=True, alpha=0.7,label='Tiempo Total (Cola Única)')
    plt.title('Distribución de Tiempos Totales (Cola Única)')
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Densidad')
    plt.legend()
    plt.savefig('single_queue_times.png')
    plt.close()

def main():
    avg_separate, avg_single, t_separate, t_single = run_simulation()
    print(f"Tiempo medio de estancia para colas separadas: {avg_separate:.2f} segundos")
    print(f"Tiempo medio de estancia para cola única: {avg_single:.2f} segundos")
    plot_results(t_separate, t_single)
if __name__ == "__main__":
    main()