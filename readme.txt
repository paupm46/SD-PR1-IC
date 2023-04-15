Para ejecutar automaticamente el sistema:
1 - Abrir un terminal, ejecutar "docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.11-management" y esperar a que se inicie
2 - Abrir un terminal, situarse en la carpeta del proyecto, y ejecutar ./init.sh


Para ejecutar manualmente el sistema:
1 - Abrir un terminal, ejecutar "docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.11-management" y esperar a que se inicie
2 - Abrir un terminal y ejecutar redis-server
3 - Abrir dos o más terminales, situarse en la carpeta del proyecto, y ejecutar en cada uno de ellos "python3 terminal.py"
4 - Abrir un terminal, situarse en la carpeta del proyecto, y ejecutar "python3 proxy.py"
5 - Abrir 10 o más terminales, situarse en la carpeta del proyecto, y ejecutar en cada uno de ellos "python3 compute_server.py"
6 - Abrir dos o más terminales, situarse en la carpeta del proyecto, y ejecutar en cada uno de ellos "python3 air_sensor.py"
7 - Abrir dos o más terminales, situarse en la carpeta del proyecto, y ejecutar en cada uno de ellos "python3 pollution_sensor.py"


Debe haber instalado en el sistema:
- pip3 install grpcio
- pip3 install grpcio-tools
- pip install redis
- pip install protobuf3
- pip install google-api-python-client
- python3
- rabbitmq en docker