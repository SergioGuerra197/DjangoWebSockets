import asyncio
import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer

class BingoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'bingo_room'

        # Unimos el grupo de WebSocket
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Aceptamos la conexión
        await self.accept()

        # Generar la tarjeta de bingo para el usuario
        self.user_bingo_card = self.generate_bingo_card()

        # Enviar la tarjeta de bingo al cliente
        await self.send(text_data=json.dumps({
            'type': 'bingo_card',
            'card': self.user_bingo_card
        }))

        # Iniciar el envío periódico de números aleatorios
        self.random_number_task = asyncio.create_task(self.send_random_number())

    async def disconnect(self, close_code):
        # Dejar el grupo cuando el WebSocket se cierre
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Cancelamos el envío periódico cuando se desconecte
        if hasattr(self, 'random_number_task'):
            self.random_number_task.cancel()

    async def receive(self, text_data):
        # Recibir mensaje desde WebSocket (en este caso no se usa)
        pass

    def generate_bingo_card(self):
        """
        Genera una tarjeta de bingo aleatoria con las reglas estándar:
        - B: 1-15
        - I: 16-30
        - N: 31-45 (espacio libre en el centro)
        - G: 46-60
        - O: 61-75
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

        # Retornar la tarjeta con números aleatorios
        return bingo_card

    async def send_random_number(self):
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

            # Elegir un número aleatorio dentro del rango
            random_number = random.choice(number_range)

            # Enviar el número aleatorio a todos los clientes conectados
            await self.send_random_number_to_group(letter, random_number)

            # Esperar 5 segundos antes de enviar otro número
            await asyncio.sleep(5)

    # Nueva función para enviar el número aleatorio al grupo
    async def send_random_number_to_group(self, letter, random_number):
        # Enviar el número aleatorio a todos los usuarios conectados
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'receive_random_number',  # Cambio de tipo de mensaje
                'letter': letter,
                'random_number': random_number
            }
        )

    # Recibir mensaje desde el grupo
    async def receive_random_number(self, event):
        # Recibir la letra y el número aleatorio
        letter = event['letter']
        random_number = event['random_number']

        # Enviar el número aleatorio al WebSocket
        await self.send(text_data=json.dumps({
            'letter': letter,
            'random_number': random_number
        }))
