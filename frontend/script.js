const API_BASE = 'http://localhost:5000';

// Mine a new block
function mineBlock() {
    fetch(`${API_BASE}/mine`)
        .then(response => response.json())
        .then(data => {
            alert(`Success: ${data.message}`);
            fetchChain(); // Refresh the chain
        })
        .catch(err => alert('Error mining block: ' + err));
}

// Submit a new transaction
document.getElementById('transactionForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const sender = document.getElementById('sender').value;
    const recipient = document.getElementById('recipient').value;
    const amount = parseFloat(document.getElementById('amount').value);

    fetch(`${API_BASE}/transactions/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sender, recipient, amount })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById('transactionForm').reset();
    })
    .catch(err => alert('Error creating transaction: ' + err));
});

// Load the full chain
function fetchChain() {
    fetch(`${API_BASE}/chain`)
        .then(response => response.json())
        .then(data => {
            const chainDiv = document.getElementById('chain');
            chainDiv.innerHTML = '';
            data.chain.forEach(block => {
                const blockDiv = document.createElement('div');
                blockDiv.className = 'block';
                blockDiv.innerHTML = `
                    <h3>Block ${block.index}</h3>
                    <p><b>Timestamp:</b> ${new Date(block.timestamp * 1000).toLocaleString()}</p>
                    <p><b>Proof:</b> ${block.proof}</p>
                    <p><b>Previous Hash:</b> ${block.previous_hash}</p>
                    <p><b>Transactions:</b><pre>${JSON.stringify(block.transactions, null, 2)}</pre></p>
                `;
                chainDiv.appendChild(blockDiv);
            });
        })
        .catch(err => alert('Error loading chain: ' + err));
}

// Load chain on page load
fetchChain();
