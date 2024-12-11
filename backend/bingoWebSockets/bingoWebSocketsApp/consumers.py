import asyncio
import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer

class BingoConsumer(AsyncWebsocketConsumer):
    
    # Variable de clase para controlar la tarea de envío de números aleatorios
    random_number_task = None

    # Diccionario de clase para almacenar los números generados
    generated_numbers = {
        'B': [],
        'I': [],
        'N': [],
        'G': [],
        'O': []
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_bingo_card = None  # Tarjeta de Bingo del cliente
        self.last_generated_number = None  # Último número generado (letra y número)

    async def connect(self):
        """
        Maneja la conexión de un cliente al WebSocket.
        """
        self.room_group_name = 'bingo_room'

        # Unir al cliente al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Aceptar la conexión
        await self.accept()

        # Generar y enviar la tarjeta de Bingo al cliente
        self.user_bingo_card = self.generate_bingo_card()
        await self.send(text_data=json.dumps({
            'type': 'bingo_card',
            'card': self.user_bingo_card
        }))

         # Si hay un número previamente generado, enviarlo al cliente
        if self.last_generated_number:
            await self.send(text_data=json.dumps({
                'type': 'last_number',
                'letter': self.last_generated_number['letter'],
                'number': self.last_generated_number['number']
            }))

        # Iniciar la tarea de envío de números si aún no está corriendo
        if BingoConsumer.random_number_task is None:
            BingoConsumer.random_number_task = asyncio.create_task(self.send_random_number())

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

    def generate_bingo_card(self):
        """
        Genera una tarjeta de Bingo aleatoria.
        """
        bingo_card = {
            'B': random.sample(range(1, 16), 5),
            'I': random.sample(range(16, 31), 5),
            'N': random.sample(range(31, 46), 5),
            'G': random.sample(range(46, 61), 5),
            'O': random.sample(range(61, 76), 5),
        }
        bingo_card['N'][2] = "Free"
        return bingo_card

    async def send_random_number(self):
        """
        Envía números aleatorios a todos los clientes conectados.
        """
        try:
            while True:
                # Verificar si hay más números para enviar
                if all(len(self.get_remaining_numbers(letter)) == 0 for letter in ['B', 'I', 'N', 'G', 'O']):
                    print("No hay más números disponibles. Deteniendo el servidor.")
                    print(self.generated_numbers)
                    break  # Rompe el ciclo cuando no hay más números

                # Elegir una letra aleatoria entre B, I, N, G, O
                letter = random.choice(['B', 'I', 'N', 'G', 'O'])

                # Elegir el rango de números para esa letra
                number_range = self.get_number_range(letter)

                # Filtrar los números que ya han sido generados
                remaining_numbers = self.get_remaining_numbers(letter)

                # Si no hay números disponibles, continuar con la siguiente letra
                if not remaining_numbers:
                    continue

                # Elegir un número aleatorio
                random_number = random.choice(remaining_numbers)

                # Guardar el número generado
                self.generated_numbers[letter].append(random_number)

                self.last_generated_number = {'letter': letter, 'number': random_number}

                # Enviar el número a todos los clientes
                await self.send_random_number_to_group(letter, random_number,self.generated_numbers)

                # Esperar antes de enviar otro número
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            print("El ciclo ha sido cancelado.")
            return  # Permite que el servidor se detenga adecuadamente
        
    def get_number_range(self, letter):
        if letter == 'B':
            return range(1, 16)
        elif letter == 'I':
            return range(16, 31)
        elif letter == 'N':
            return range(31, 46)
        elif letter == 'G':
            return range(46, 61)
        else:
            return range(61, 76)
        
    def get_remaining_numbers(self, letter):
    # Filtrar los números no generados
        return list(set(self.get_number_range(letter)) - set(self.generated_numbers[letter]))

    async def send_random_number_to_group(self, letter, random_number, generated_numbers):
        """
        Envía un número aleatorio con su letra correspondiente a todos los usuarios.
        """
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'receive_random_number',
                'letter': letter,
                'random_number': random_number,
                'generated_numbers':generated_numbers
            }
        )

    async def receive_random_number(self, event):
        """
        Recibe un número aleatorio del grupo y lo envía al cliente WebSocket.
        """
        await self.send(text_data=json.dumps({
            'letter': event['letter'],
            'random_number': event['random_number'],
            'generated_numbers': event['generated_numbers']
        }))

    async def receive(self, text_data):

        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "check_number":
            number = data.get("number")

            # Verificar si el número fue generado
            for letter, numbers in self.generated_numbers.items():
                if number in numbers:
                    # Responder al cliente indicando que el número ya fue generado
                    await self.send(text_data=json.dumps({
                        "type": "number_status",
                        "status": "generated",
                        "number": number
                    }))
                    return

            # Responder al cliente indicando que el número no ha sido generado
            await self.send(text_data=json.dumps({
                "type": "number_status",
                "status": "not_generated",
                "number": number
            }))

        elif message_type == "bingo":
            bingo_card = data.get("card")
            bingo = None
            generated_numbers_set = set(num for nums in self.generated_numbers.values() for num in nums)

            # Verificar las filas
            for row in zip(*[bingo_card[letter] for letter in ['B', 'I', 'N', 'G', 'O']]):
                if all(num in generated_numbers_set or num == "Free" for num in row):
                    bingo = True  # Si una fila tiene bingo, se devuelve True
                    break  # Salir del ciclo si encontramos un bingo en las filas
            
            # Verificar las columnas solo si no se encontró bingo en las filas
            if not bingo:
                for col in bingo_card.values():
                    if all(num in generated_numbers_set or num == "Free" for num in col):
                        bingo = True  # Si una columna tiene bingo, se devuelve True
                        break  # Salir del ciclo si encontramos un bingo en las columnas

            # Si hay un bingo, notificar al ganador y a los demás
            if bingo:
                # Enviar mensaje al ganador
                await self.send(text_data=json.dumps({
                    "type": "bingo_winner",
                    "winner": self.channel_name,  # El canal del ganador
                    "message": "¡Ganaste!",  # Mensaje para el ganador
                    "is_winner": True
                }))

                # Enviar mensaje a todos los demás jugadores (indicando que hubo un ganador)
                await self.channel_layer.group_send(
                    self.room_group_name,  # Nombre del grupo de WebSocket
                    {
                        "type": "bingo_winner",  # Tipo de mensaje
                        "winner": self.channel_name,  # El canal del ganador
                        "message": "Ya hubo un ganador.",  # Mensaje para los demás
                        "is_winner": False
                    }
                )

                # Detener cualquier tarea de números aleatorios si se genera un ganador
                if BingoConsumer.random_number_task:
                    BingoConsumer.random_number_task.cancel()
                    BingoConsumer.random_number_task = None
    
    async def bingo_winner(self, event):
        """
        Notifica a todos los clientes que alguien ha ganado.
        """
        # Verifica si el mensaje es para el ganador o para los demás
        if event.get("is_winner", False):
            message = "¡Ganaste!"
        else:
            message = "Ya hubo un ganador."

        # Enviar el mensaje al cliente que pertenece a este consumidor
        await self.send(text_data=json.dumps({
            "type": "bingo_winner",
            "winner": event["winner"],  # El canal del ganador
            "message": message  # El mensaje correspondiente
        }))