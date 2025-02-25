<script>
    import { onMount } from "svelte";
  </script>
  
  <nav class="navbar">
    <div class="logo">Codect</div>
    <ul class="nav-links">
      <li><a href="/">Home</a></li>
      <li><a href="/features">Features</a></li>
      <li><a href="/pricing">Pricing</a></li>
      <li><a href="/contact">Contact</a></li>
    </ul>
    <button class="cta-btn" on:click={() => document.getElementById('modalOverlay').style.display = 'flex'}>
      Try It Now
    </button>
  </nav>
  
  <style>
    /* Add your CSS styles here */
  </style>
  