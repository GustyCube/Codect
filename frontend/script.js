// Popup modal elements
const openModalBtn = document.getElementById('openModalBtn');
const modalOverlay = document.getElementById('modalOverlay');
const closeModalBtn = document.getElementById('closeModalBtn');
const tryBtn = document.getElementById('tryBtn');

// Open modal
function openModal() {
  modalOverlay.style.display = 'flex';
}

// Close modal
function closeModal() {
  modalOverlay.style.display = 'none';
}

// Event listeners
openModalBtn.addEventListener('click', openModal);
tryBtn.addEventListener('click', openModal);
closeModalBtn.addEventListener('click', closeModal);

// Close modal when clicking outside its content
window.addEventListener('click', (event) => {
  if (event.target === modalOverlay) {
    closeModal();
  }
});
