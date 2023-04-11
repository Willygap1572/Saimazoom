#!/bin/bash
echo "Iniciando test..."
# Define una función que ejecuta una llamada a Python y redirige la salida a un archivo
function run_python {
    python "$1" > salida_$2.txt
}

# Exporta la función para que pueda ser utilizada por parallel
export -f run_python

# Lanza una instancia de launch_controler.py
python launch_controler.py -l false > salida_controler.txt &

# Lanza tres instancias de launch_robot.py
parallel run_python ::: launch_robot.py launch_robot.py launch_robot.py ::: robot1 robot2 robot3

# Lanza cinco instancias de launch_delivery.py
parallel run_python ::: launch_delivery.py launch_delivery.py launch_delivery.py launch_delivery.py launch_delivery.py ::: delivery1 delivery2 delivery3 delivery4 delivery5

# Lanza cinco instancias de launch_client.py
parallel run_python ::: launch_client.py launch_client.py launch_client.py launch_client.py launch_client.py ::: client1 client2 client3 client4 client5