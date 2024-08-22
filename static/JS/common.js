fetch('/api/data')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        data.forEach(user => {
            console.log(`User: ${user.name}, ID: ${user.id}`);
        });
    })
    .catch(error => console.error('There was a problem with the fetch operation:', error));
