function classifySoil() {
  const form = document.getElementById('soilForm');
  const data = new FormData(form);

  fetch('/classify', {
    method: 'POST',
    body: data
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(result => {
    document.getElementById('classificationResult').innerText = result.classification;
    document.getElementById('piResult').innerText = `Plasticity Index (PI): ${result.pi}`;
    document.getElementById('alineResult').innerText = `A-Line Value: ${result.aline}`;
    document.getElementById('resultPopup').style.display = 'block';
  })
  .catch(error => {
    alert('Error classifying soil: ' + error.message);
    console.error('Error:', error);
  });
}

function addSampleForm() {
  const form = document.getElementById('soilForm');
  const formClone = form.cloneNode(true);

  // Prevent duplicate IDs
  formClone.id = ''; // Clear the cloned form's ID

  // Optional: Reset input values
  formClone.querySelectorAll('input').forEach(input => input.value = '');

  document.body.appendChild(formClone);
}

function closePopup() {
  document.getElementById('resultPopup').style.display = 'none';
}
