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

    // Marcar el número en la tarjeta de bingo
};

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
    bingoCardContainer.innerHTML = ""; // Limpia cualquier tarjeta previa

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
            td.textContent = bingoCard[col][row];
            if (col === 'N' && row === 2) { // Casilla central
                td.textContent = 'FREE';
                td.classList.add("free");
            }
            td.id = `${row}-${colIndex}`;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    }

    table.appendChild(tbody);
    bingoCardContainer.appendChild(table);
}
