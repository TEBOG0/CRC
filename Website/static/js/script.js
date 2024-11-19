// Event listener to alerts
setTimeout(function () {
            const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        alertContainer.style.opacity = '0';
                setTimeout(() => alertContainer.remove(), 500);
            }
}, 4000);


// Event listener to format the card number
document.getElementById('card-number').addEventListener('input', function (e) {
    const input = e.target;
    let value = input.value.replace(/\D/g, ''); // Remove non-numeric characters
    const formattedValue = value.match(/.{1,4}/g)?.join(' ') || value; // Group into chunks of 4
    input.value = formattedValue;
});
