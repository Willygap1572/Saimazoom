import src.client as c
import os
import sys

def console(client):
    while True:
        print('1. Register')
        print('2. Order products')
        print('3. Cancel order')
        print('4. Show orders')
        print('5. Exit')
        option = input('Choose an option: ')
        if option == '1':
            client.client_register()
        elif option == '2':
            products = input('Products separated by commas (product1,product2,...): ')
            client.order_products(products.split(','))
        elif option == '3':
            order_id = input('Order id: ')
            client.cancel_order(order_id)
        elif option == '4':
            client.see_orders()
        elif option == '5':
            break
        else:
            print('Invalid option')

if __name__ == '__main__':
    client = c.Client()
    try:
        console(client)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)