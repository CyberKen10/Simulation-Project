import simpy
import random
import numpy as np
import matplotlib.pyplot as plt 

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
# Parámetros de la simulación
LAMBDA = 60 / 3600  
MU = 1 / 150       
SIM_TIME = 8 * 3600 
NUM_SERVERS = 3         

def customer_separate(env, queue_id, queues, total_times):
    arrive = env.now
    with queues[queue_id].request() as req:
        yield req
        wait = env.now - arrive
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

def customer_single(env, queue, total):
    arrive = env.now
    with queue.request() as req:
        yield req
        # Espera hasta obtener un servidor
        yield env.timeout(random.expovariate(MU))  # Simula el servicio
    total_time = env.now - arrive  # Tiempo total (espera + servicio)
    total_time.append(total_time)

def setup_single_queue(env, num_servers):
    queue = simpy.Resource(env, capacity=num_servers)
    return queue

def arrive_single(env, queue, wait_times):
    while True:
        yield env.timeout(random.expovariate(LAMBDA))
        env.process(customer_single(env, queue, wait_times))

def run_simulation():
    env1 = simpy.Environment()
    queues = setup_separate_queues(env1, NUM_SERVERS)
    total_times_separate = []
    env1.process(arrive_separate(env1, queues, total_times_separate))
    env1.run(until=SIM_TIME)
    avg_time_separate = np.mean(total_times_separate) if total_times_separate else 0
    env2 = simpy.Environment()
    queue = setup_single_queue(env2, NUM_SERVERS)
    wait_times_single = []
    env2.process(arrive_single(env2, queue, wait_times_single))
    env2.run(until=SIM_TIME)
    avg_wait_single = np.mean(wait_times_single) if wait_times_single else 0
    return avg_time_separate, avg_wait_single, total_times_separate, wait_times_single

def plot_results(total_times_separate, wait_times_single):
    plt.figure(figsize=(10, 6))
    plt.hist(total_times_separate, bins=50, density=True, alpha=0.7,label='Tiempo Total (Colas Separadas)')
    plt.title('Distribución de Tiempos Totales (Colas Separadas)')
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Densidad')
    plt.legend()
    plt.savefig('separate_queues_times.png')
    plt.close()
    plt.figure(figsize=(10, 6))
    plt.hist(wait_times_single, bins=50, density=True, alpha=0.7,label='Tiempo de Espera (Cola Única)')
    plt.title('Distribución de Tiempos de Espera (Cola Única)')
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Densidad')
    plt.legend()
    plt.savefig('single_queue_wait_times.png')
    plt.close()

def main():
    avg_time_separate, avg_wait_single, total_times_separate, wait_times_single = run_simulation()
    print(f"Tiempo medio de estancia para colas separadas: {avg_time_separate:.2f} segundos")
    print(f"Tiempo medio de espera para cola única: {avg_wait_single:.2f} segundos")
    plot_results(total_times_separate, wait_times_single)

if __name__ == "__main__":
    main()
