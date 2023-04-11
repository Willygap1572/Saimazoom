import src.robot as r
import sys
import os
import json

def main():
    
    # leer fichero de configuracion saimazoom_config.json
    with open('saimazoom_config.json') as json_file:
        data = json.load(json_file)
        p_almacen = data['p_almacen'] or 0.95
    robot = r.Robot(p_almacen)
    robot.channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)