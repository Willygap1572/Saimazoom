import src.delivery as d
import json
import sys
import os

def main():
    # leer fichero de configuracion saimazoom_config.json
    with open('saimazoom_config.json') as json_file:
        data = json.load(json_file)
        p_entrega = data['p_entrega'] or 0.95
    delivery = d.Delivery(p_entrega)
    delivery.channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)