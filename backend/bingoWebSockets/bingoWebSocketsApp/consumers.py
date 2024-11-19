import asyncio
import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer

class BingoConsumer(AsyncWebsocketConsumer):
    """
    Esta clase maneja la lógica del WebSocket para un juego de Bingo en tiempo real.
    Los jugadores se conectan a través de WebSockets y reciben una tarjeta de Bingo
    personalizada y números aleatorios a medida que se eligen.
    """
    
    async def connect(self):
        """
        Método llamado cuando un cliente intenta conectarse al WebSocket.
        Aquí se une el cliente al grupo de WebSocket y se le envía su tarjeta de Bingo.
        """
        self.room_group_name = 'bingo_room'

        # Unir al cliente al grupo de WebSocket para enviar y recibir mensajes en grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Aceptar la conexión WebSocket
        await self.accept()

        # Generar una tarjeta de Bingo personalizada para el cliente
        self.user_bingo_card = self.generate_bingo_card()

        # Enviar la tarjeta de Bingo al cliente en formato JSON
        await self.send(text_data=json.dumps({
            'type': 'bingo_card',  # Tipo de mensaje
            'card': self.user_bingo_card  # La tarjeta generada
        }))

        # Iniciar el envío periódico de números aleatorios
        self.random_number_task = asyncio.create_task(self.send_random_number())

    async def disconnect(self, close_code):
        """
        Método llamado cuando un cliente se desconecta del WebSocket.
        Aquí se elimina al cliente del grupo y se cancela el envío de números aleatorios.
        """
        # Dejar el grupo cuando el WebSocket se cierre
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Cancelar el envío periódico de números aleatorios si el cliente se desconecta
        if hasattr(self, 'random_number_task'):
            self.random_number_task.cancel()

    async def receive(self, text_data):
        """
        Método para manejar los mensajes recibidos desde el WebSocket.
        Actualmente no se utiliza, pero se puede ampliar en el futuro para interactuar con el cliente.
        """
        pass

    def generate_bingo_card(self):
        """
        Genera una tarjeta de Bingo aleatoria siguiendo las reglas estándar:
        - B: 1-15
        - I: 16-30
        - N: 31-45 (espacio libre en el centro)
        - G: 46-60
        - O: 61-75
        
        Devuelve un diccionario con las letras y sus respectivos números.
        """
        bingo_card = {
            'B': random.sample(range(1, 16), 5),
            'I': random.sample(range(16, 31), 5),
            'N': random.sample(range(31, 46), 5),
            'G': random.sample(range(46, 61), 5),
            'O': random.sample(range(61, 76), 5),
        }

        # Dejar el centro vacío en la columna N (espacio libre en el centro)
        bingo_card['N'][2] = "Free"

        # Retornar la tarjeta generada
        return bingo_card

    async def send_random_number(self):
        """
        Envia números aleatorios periódicamente a todos los clientes conectados.
        Cada número pertenece a una de las cinco columnas del Bingo: B, I, N, G, O.
        Los números se eligen aleatoriamente dentro de los rangos correspondientes.
        """
        while True:
            # Elegir una letra aleatoria entre B, I, N, G, O
            letter = random.choice(['B', 'I', 'N', 'G', 'O'])

            # Determinar el rango según la letra
            if letter == 'B':
                number_range = range(1, 16)
            elif letter == 'I':
                number_range = range(16, 31)
            elif letter == 'N':
                number_range = range(31, 46)
            elif letter == 'G':
                number_range = range(46, 61)
            else:
                number_range = range(61, 76)

            # Elegir un número aleatorio dentro del rango de la letra seleccionada
            random_number = random.choice(number_range)

            # Enviar el número aleatorio a todos los clientes conectados
            await self.send_random_number_to_group(letter, random_number)

            # Esperar 5 segundos antes de enviar otro número
            await asyncio.sleep(5)

    async def send_random_number_to_group(self, letter, random_number):
        """
        Envía un número aleatorio con su letra correspondiente a todos los usuarios
        conectados al grupo del WebSocket.
        
        :param letter: La letra que corresponde a la columna del número (B, I, N, G, O)
        :param random_number: El número aleatorio a enviar
        """
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'receive_random_number',  # Tipo de mensaje
                'letter': letter,  # Letra de la columna (B, I, N, G, O)
                'random_number': random_number  # Número aleatorio generado
            }
        )

    async def receive_random_number(self, event):
        """
        Recibe el número aleatorio y su letra correspondiente desde el grupo
        y lo envía al cliente WebSocket.
        
        :param event: El evento que contiene el número y la letra
        """
        letter = event['letter']
        random_number = event['random_number']

        # Enviar el número aleatorio al WebSocket del cliente
        await self.send(text_data=json.dumps({
            'letter': letter,  # Letra de la columna
            'random_number': random_number  # Número aleatorio
        }))
