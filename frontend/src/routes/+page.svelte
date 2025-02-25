<script>
    import Modal from "$lib/components/Modal.svelte";
</script>
<link rel="stylesheet" href="https://unicons.iconscout.com/release/v4.0.8/css/line.css">
<section class="hero">
    <div class="hero-content">
        <h1>Detect AI-Generated Code, Effortlessly & Openly</h1>
        <p>
            Codect is a free and open-source tool that helps you verify if a piece of code was written by AI.
            Run it locally, prevent scams, ensure authenticity, and enhance your coding knowledge!
        </p>
        <button class="hero-cta" on:click={() => document.getElementById('modalOverlay').style.display = 'flex'}>
            Get Started
        </button>
    </div>
    <div class="hero-image">
        <img src="/placeholder.png" alt="AI Detection">
    </div>
</section>

<Modal />

<section class="features">
    <h2>Why Choose Codect?</h2>
    <div class="features-grid">
        <div class="feature-card">
            <i class="uil uil-padlock"></i>           
                <h3>Secure & Private</h3>
            <p>Run Codect locally on your machine. Your code never leaves your device.</p>
        </div>
        <div class="feature-card">
            <i class="uil uil-bolt"></i>            
            <h3>Fast & Efficient</h3>
            <p>Instant AI code detection with no unnecessary wait times.</p>
        </div>
        <div class="feature-card">
            <i class="uil uil-brain"></i>            
            <h3>Learn & Improve</h3>
            <p>Compare human-written and AI-generated code to enhance your programming skills.</p>
        </div>
        <div class="feature-card">
            <i class="uil uil-code-branch"></i>            
            <h3>100% Open Source</h3>
            <p>Join our community of developers and contribute to the project on GitHub.</p>
        </div>
        <div class="feature-card">
            <i class="uil uil-servers"></i>            
            <h3>Run Locally or Online</h3>
            <p>Codect runs on your machine or via the cloud—your choice.</p>
        </div>
        <div class="feature-card">
            <i class="uil uil-money-bill-stack"></i>            
            <h3>Free Forever</h3>
            <p>No subscriptions, no paywalls. Just pure AI detection power for everyone.</p>
        </div>
    </div>
</section>

<section class="how-it-works">
    <h2>How It Works</h2>
    <p>Codect is simple to use. Just paste your code snippet, run the analysis, and get results instantly.</p>
    <ul>
        <li> <i class="uil uil-import" style="font-size: 1.5rem; padding-right: 15px; color: #4a90e2;"></i>Download & install Codect (or use it online).</li>
        <li><i class="uil uil-clipboard-alt" style="font-size: 1.5rem; padding-right: 15px; color: #4a90e2;"></i>Paste your code into the detection engine.</li>
        <li><i class="uil uil-file-alt" style="font-size: 1.5rem; padding-right: 15px; color: #4a90e2; "></i>Get a detailed breakdown of AI vs human-generated code patterns.</li>
    </ul>
</section>

<section class="contact">
    <h2>Get in Touch</h2>
    <p>Have questions or want to contribute? Reach out to us or join our GitHub community.</p>
    <form class="contact-form">
        <input type="text" placeholder="Name" required>
        <input type="email" placeholder="Email" required>
        <textarea rows="4" placeholder="Your Message"></textarea>
        <button type="submit">Submit</button>
    </form>
</section>
