// Conectar con el WebSocket
const socket = new WebSocket('ws://127.0.0.1:8000/ws/bingo/');

socket.onopen = () => {
    console.log('Conectado al WebSocket');
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Datos recibidos:', data);
    const letter = data.letter;
    const randomNumber = data.random_number;

    if(data.card){
        const bingoCard = data.card
        renderBingoCard(bingoCard)
    }
    // Actualizar el DOM con el número aleatorio recibido
    if (!randomNumber){
        document.getElementById('letter').textContent = `Esperando siguiente letra `;
        document.getElementById('random-number').textContent = `Esperando siguiente numero `;
    }else{
        document.getElementById('letter').textContent = `Letra: ${letter}`;
        document.getElementById('random-number').textContent = `Número: ${randomNumber}`;
    }

       // Actualizar los números generados
    if (data.generated_numbers) {
        updateGeneratedNumbers(data.generated_numbers);
    }

    // Marcar el número en la tarjeta de bingo
};

function updateGeneratedNumbers(generatedNumbers) {
    // Mostrar los números generados por letra
    Object.keys(generatedNumbers).forEach(letter => {
        const numberList = generatedNumbers[letter];
        const numberElement = document.getElementById(`generated-${letter}`);
        if (numberElement) {
            numberElement.textContent = `${letter}: ${numberList.join(', ')}`;
        }
    });
}

socket.onclose = (event) => {
    if (event.wasClean) {
        console.log(`Cerrado limpiamente: ${event.code}`);
    } else {
        console.error('Conexión cerrada de forma inesperada');
    }
};

socket.onerror = (error) => {
    console.error(`Error en el WebSocket: ${error.message}`);
};

function renderBingoCard(bingoCard) {
    const bingoCardContainer = document.getElementById("bingo-card");
    bingoCardContainer.innerHTML = ""; // Limpiar cualquier tarjeta previa

    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const tbody = document.createElement("tbody");

    // Crear la cabecera de la tabla
    const headerRow = document.createElement("tr");
    ['B', 'I', 'N', 'G', 'O'].forEach(letter => {
        const th = document.createElement("th");
        th.textContent = letter;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Crear las filas de la tabla con los números recibidos
    for (let row = 0; row < 5; row++) {
        const tr = document.createElement("tr");

        ['B', 'I', 'N', 'G', 'O'].forEach((col, colIndex) => {
            const td = document.createElement("td");
            const button = document.createElement("button");

            if (bingoCard[col] && bingoCard[col][row] !== undefined) {
                // Asignar el número a la celda correspondiente
                button.textContent = bingoCard[col][row];
            } else {
                button.textContent = ''; // Si no hay número, dejar vacío el botón
            }

            // Si es la casilla central (N), poner 'FREE' y deshabilitar el botón
            if (col === 'N' && row === 2) {
                button.textContent = 'FREE';
                button.disabled = true;
                button.classList.add("free");  // Clase para estilo especial
            }

            td.appendChild(button);  // Asegúrate de agregar el botón al td
            td.id = `${row}-${col}`;  // ID basado en la fila y la columna
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    }

    table.appendChild(tbody);
    bingoCardContainer.appendChild(table);
}
