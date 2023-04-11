import src.controler as c
import sys
import os
import json
import argparse

#saves a state of the controler in a file
def save_state(controler):
    with open('state.json', 'w') as f:
        json.dump(controler.content_dict(), f)
    

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Controlador de Saimazoom, el mejor servicio de compras online')
    parser.add_argument('-l','--load', type=str, help='Usage:\n\t -l true si se quiere cargar el archivo state.json\n\t -l false si quieres que empiece de 0.', required=True)
    args = parser.parse_args()
    controler = c.Controler()
    if args.load == 'true':
        with open('state.json', 'r') as f:
            controler.content_load(json.load(f))
    try:
        controler.channel.start_consuming()
    except KeyboardInterrupt:
        save_state(controler)
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

