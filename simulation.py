import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Establecer la semilla para la reproducibilidad
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
# Parámetros de la simulación
LAMBDA = 60 / 3600   # Tasa de llegada: 60 clientes por hora (clientes/segundo)
MU = 1 / 150         # Tasa de servicio: tiempo medio de 150 segundos
SIM_TIME = 8 * 3600  # Tiempo de simulación: 8 horas (en segundos)
NUM_SERVERS = 3      # Número de servidores
RECORD_INTERVAL = 60  # Intervalo para monitorear colas (segundos)
# Valores teóricos para comparación
THEORY_SEPARATE = 900    # Tiempo medio teórico para colas separadas (segundos)
THEORY_SINGLE = 360.6    # Tiempo medio teórico para cola única (segundos)

# Escenario 1: Tres colas separadas (M/M/1)
def customer_separate(env, queue_id, queues, total_times):
    arrive = env.now
    with queues[queue_id].request() as req:
        yield req
        yield env.timeout(random.expovariate(MU))
    departure = env.now
    total_time = departure - arrive
    total_times.append((departure, total_time))

def setup_separate_queues(env, num_queues):
    return [simpy.Resource(env, capacity=1) for _ in range(num_queues)]

def arrive_separate(env, queues, total_times):
    while True:
        yield env.timeout(random.expovariate(LAMBDA))
        queue_id = random.randint(0, len(queues) - 1)
        env.process(customer_separate(env, queue_id, queues, total_times))

def monitor_separate_queues(env, queues, interval, records):
    while True:
        for i, queue in enumerate(queues):
            queue_length = len(queue.queue)
            records[i].append((env.now, queue_length))
        yield env.timeout(interval)

# Escenario 2: Una cola única con tres servidores (M/M/3)
def customer_single(env, queue, total_times):
    arrive = env.now
    with queue.request() as req:
        yield req
        yield env.timeout(random.expovariate(MU))
    departure = env.now
    total_time = departure - arrive
    total_times.append((departure, total_time))

def setup_single_queue(env, num_servers):
    return simpy.Resource(env, capacity=num_servers)

def arrive_single(env, queue, total_times):
    while True:
        yield env.timeout(random.expovariate(LAMBDA))
        env.process(customer_single(env, queue, total_times))

def monitor_single_queue(env, queue, interval, queue_records):
    while True:
        queue_length = len(queue.queue)
        queue_records.append((env.now, queue_length))
        yield env.timeout(interval)

def run_simulation():
    # Simulación para tres colas separadas
    env1 = simpy.Environment()
    queues = setup_separate_queues(env1, NUM_SERVERS)
    total_times_separate = []
    queue_lengths_separate = [[] for _ in range(NUM_SERVERS)]
    env1.process(arrive_separate(env1, queues, total_times_separate))
    env1.process(monitor_separate_queues(env1, queues, RECORD_INTERVAL, queue_lengths_separate))
    env1.run(until=SIM_TIME)
    departures_separate, times_separate = zip(*total_times_separate) if total_times_separate else ([], [])
    avg_time_separate = np.mean(times_separate) if times_separate else 0
    # Simulación para una cola única
    env2 = simpy.Environment()
    queue = setup_single_queue(env2, NUM_SERVERS)
    total_times_single = []
    queue_lengths_single = []
    env2.process(arrive_single(env2, queue, total_times_single))
    env2.process(monitor_single_queue(env2, queue, RECORD_INTERVAL, queue_lengths_single))
    env2.run(until=SIM_TIME)
    departures_single, times_single = zip(*total_times_single) if total_times_single else ([], [])
    avg_time_single = np.mean(times_single) if times_single else 0

    return (avg_time_separate, avg_time_single, total_times_separate, total_times_single,
            queue_lengths_separate, queue_lengths_single)

# Función para graficar resultados 
def plot_results(total_times_separate, total_times_single, queue_lengths_separate, queue_lengths_single):
    _, times_separate = zip(*total_times_separate) if total_times_separate else ([], [])
    _, times_single = zip(*total_times_single) if total_times_single else ([], [])
    # Promedio acumulado
    cum_avg_separate = np.cumsum(times_separate) / np.arange(1, len(times_separate) + 1) if times_separate else []
    cum_avg_single = np.cumsum(times_single) / np.arange(1, len(times_single) + 1) if times_single else []
    plt.figure(figsize=(10, 6))
    if len(times_separate) > 0:  # Cambiado de if cum_avg_separate a if len(times_separate) > 0
        plt.plot(range(1, len(cum_avg_separate) + 1), cum_avg_separate, label='Colas Separadas')
    if len(times_single) > 0:    # Cambiado de if cum_avg_single a if len(times_single) > 0
        plt.plot(range(1, len(cum_avg_single) + 1), cum_avg_single, label='Cola Única')
    plt.axhline(THEORY_SEPARATE, color='r', linestyle='--', label='Teórico Colas Separadas')
    plt.axhline(THEORY_SINGLE, color='g', linestyle='--', label='Teórico Cola Única')
    plt.xlabel('Número de Cliente')
    plt.ylabel('Promedio Acumulado (segundos)')
    plt.title('Promedio Acumulado de Tiempos Totales')
    plt.legend()
    plt.savefig('cumulative_avg.png')
    plt.close()
    # Longitudes de colas separadas
    plt.figure(figsize=(12, 6))
    for i in range(NUM_SERVERS):
        if queue_lengths_separate[i]:
            times, lengths = zip(*queue_lengths_separate[i])
            plt.plot(times, lengths, label=f'Cola {i+1}')
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Longitud de la Cola')
    plt.title('Longitud de Colas Separadas a lo Largo del Tiempo')
    plt.legend()
    plt.savefig('separate_queue_lengths.png')
    plt.close()
    # Longitud de cola única
    if queue_lengths_single:
        times, lengths = zip(*queue_lengths_single)
        plt.figure(figsize=(10, 6))
        plt.plot(times, lengths, label='Cola Única')
        plt.xlabel('Tiempo (segundos)')
        plt.ylabel('Longitud de la Cola')
        plt.title('Longitud de la Cola Única a lo Largo del Tiempo')
        plt.legend()
        plt.savefig('single_queue_length.png')
        plt.close()
    # Gráfico de barras para promedios
    averages = [np.mean(times_separate) if times_separate else 0,
                np.mean(times_single) if times_single else 0]
    labels = ['Colas Separadas', 'Cola Única']
    plt.figure(figsize=(8, 6))
    plt.bar(labels, averages, color=['blue', 'green'])
    plt.ylabel('Tiempo Medio (segundos)')
    plt.title('Comparación de Tiempos Medios')
    plt.savefig('bar_comparison.png')
    plt.close()

def main():
    (avg_separate, avg_single, total_times_separate, total_times_single,
     queue_lengths_separate, queue_lengths_single) = run_simulation()
    print(f"Tiempo medio de estancia para colas separadas: {avg_separate:.2f} segundos")
    print(f"Tiempo medio de estancia para cola única: {avg_single:.2f} segundos")
    plot_results(total_times_separate, total_times_single, queue_lengths_separate, queue_lengths_single)

if __name__ == "__main__":
    main()