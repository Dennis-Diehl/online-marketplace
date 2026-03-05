
function fetchEntities() {
    fetch('/api/entities')
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error fetching entities:', error));
}

function createEntity(entityData) {
    fetch('/api/entities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(entityData)
    })
    .then(response => response.json())
    .then(data => console.log('Created entity:', data))
    .catch(error => console.error('Error creating entity:', error));
}

function updateEntity(id, updatedData) {
    fetch(`/api/entities/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedData)
    })
    .then(response => response.json())
    .then(data => console.log('Updated entity:', data))
    .catch(error => console.error('Error updating entity:', error));
}

function deleteEntity(id) {
    fetch(`/api/entities/${id}`, {
        method: 'DELETE'
    })
    .then(() => console.log('Deleted entity with ID:', id))
    .catch(error => console.error('Error deleting entity:', error));
}


