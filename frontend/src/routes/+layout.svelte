<script>
	import Navbar from "$lib/components/Navbar.svelte";
	import Footer from "$lib/components/Footer.svelte";
	// import a stylesheet that is $lib/styles/global.css AI!
	import "$lib/styles/global.css";
	// make sure that this is properly imported as a stylesheet

  </script>
  
  <Navbar />
  <slot />  <!-- Page content loads here -->
  <Footer />
  