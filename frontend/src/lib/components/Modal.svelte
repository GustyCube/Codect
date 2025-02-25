<script>
    function closeModal() {
      document.getElementById('modalOverlay').style.display = 'none';
    }
  </script>
  
  <div class="modal" id="modalOverlay">
    <div class="modal-content">
      <span class="close-btn" on:click={closeModal}>&times;</span>
      <h2>Try Codect Now</h2>
      <p>Enter a snippet of code below and let Codect analyze whether it was written by a human or AI.</p>
      <textarea rows="5" placeholder="Paste your code here..."></textarea>
      <button class="analyze-btn">Analyze Code</button>
    </div>
  </div>
  
  <style>
    /* Add your modal CSS here */
  </style>
  