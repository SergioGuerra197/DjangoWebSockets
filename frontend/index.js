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

    // Actualizar el DOM con el número aleatorio recibido
    document.getElementById('letter').textContent = `Letra: ${letter}`;
    document.getElementById('random-number').textContent = `Número: ${randomNumber}`;

    // Marcar el número en la tarjeta de bingo
    markNumber(letter, randomNumber);
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

// Función para cargar la tarjeta de bingo
function loadBingoCard() {
    const bingoCard = generateBingoCard();
    const bingoCardContainer = document.getElementById("bingo-card");

    // Crear una tabla para la tarjeta de bingo
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

    // Crear las filas de la tabla con los números generados
    bingoCard.forEach((row, rowIndex) => {
        const tr = document.createElement("tr");
        row.forEach((num, colIndex) => {
            const td = document.createElement("td");
            td.textContent = num;
            if (rowIndex === 2 && colIndex === 2) { // La casilla central es libre
                td.classList.add("free");
                td.textContent = 'Free';
            }
            td.id = `${rowIndex}-${colIndex}`; // Asignar ID único para cada celda
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    bingoCardContainer.appendChild(table);
}

// Función para generar la tarjeta de bingo con números aleatorios
function generateBingoCard() {
    const card = [];
    const columns = {
        B: [1, 15],
        I: [16, 30],
        N: [31, 45],
        G: [46, 60],
        O: [61, 75],
    };

    // Generar 5 filas, cada una con 5 números
    for (let row = 0; row < 5; row++) {
        const rowValues = [];
        for (let col of Object.keys(columns)) {
            const range = columns[col];
            const randomNumber = getRandomNumber(range[0], range[1]);
            rowValues.push(randomNumber);
        }
        card.push(rowValues);
    }

    // Reemplazar el valor central con 'FREE'
    card[2][2] = 'FREE';
    
    return card;
}

// Función para obtener un número aleatorio en un rango específico
function getRandomNumber(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Función para marcar el número en la tarjeta de bingo
function markNumber(letter, randomNumber) {
    const columnIndex = getColumnIndex(letter);
    const table = document.querySelector("table");

    for (let row = 0; row < 5; row++) {
        const cell = table.rows[row].cells[columnIndex];
        if (parseInt(cell.textContent) === randomNumber) {
            cell.classList.add("marked");
        }
    }
}

// Función para obtener el índice de la columna (B=0, I=1, N=2, G=3, O=4)
function getColumnIndex(letter) {
    switch (letter) {
        case 'B': return 0;
        case 'I': return 1;
        case 'N': return 2;
        case 'G': return 3;
        case 'O': return 4;
        default: return -1;
    }
}

// Llamar a la función para cargar la tarjeta al cargar la página
window.onload = function() {
    loadBingoCard();
};
