# Simulación de Sistemas de Colas 

## Introducción

En este proyecto, se analiza el sistema de atención al cliente en el local de comida rápida "Panis" mediante simulación. Se comparan dos configuraciones de colas: una con tres colas separadas, cada una atendida por un empleado, y otra con una única cola que distribuye clientes a los tres empleados. El objetivo es determinar cuál configuración minimiza el tiempo medio que un cliente pasa en el sistema.

## Código

El código de la simulación se encuentra en el archivo [`simulacion_panis.py`](simulation.py). Incluye funciones para definir los procesos de clientes, servidores y monitoreo de colas, así como la ejecución de las simulaciones y la generación de gráficos.

## Dependencias

- Python 3.x
- SimPy
- NumPy
- Matplotlib

## Ejecución

Para ejecutar la simulación, clone el repositorio y ejecute el siguiente comando:
```bash
python simulacion_panis.py