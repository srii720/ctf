/**
 * Self-contained Confetti Animation Module
 * Usage: window.launchConfetti() — shoots confetti for ~3 seconds then cleans up
 */
(function() {
  const COLORS = ['#00ff88', '#00e5ff', '#a855f7', '#ffd93d', '#ff4757', '#ffffff'];
  const PARTICLE_COUNT = 120;
  const DURATION_MS = 3200;

  class Particle {
    constructor(canvasWidth, canvasHeight) {
      // Launch from bottom-middle area with spread
      this.x = canvasWidth * 0.5 + (Math.random() - 0.5) * (canvasWidth * 0.3);
      this.y = canvasHeight * 0.65 + (Math.random() - 0.5) * 50;

      // Random velocities: upward burst with horizontal dispersal
      const angle = (Math.random() * Math.PI * 0.8) + (Math.PI * 0.1); // upward arc
      const speed = Math.random() * 14 + 10;
      this.vx = Math.cos(angle) * (Math.random() > 0.5 ? speed : -speed) * 0.8;
      this.vy = -Math.sin(angle) * speed - (Math.random() * 5 + 4);

      this.gravity = 0.38;
      this.friction = 0.985;

      this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
      this.width = Math.random() * 10 + 6;
      this.height = Math.random() * 6 + 4;

      this.rotation = Math.random() * 360;
      this.rotationSpeed = (Math.random() - 0.5) * 12;
      this.wobble = Math.random() * Math.PI * 2;
      this.wobbleSpeed = Math.random() * 0.1 + 0.05;

      this.opacity = 1;
      this.shape = Math.random() > 0.3 ? 'rect' : 'circle';
    }

    update(progress) {
      this.vx *= this.friction;
      this.vy += this.gravity;
      this.vy *= this.friction;

      this.x += this.vx;
      this.y += this.vy;

      this.rotation += this.rotationSpeed;
      this.wobble += this.wobbleSpeed;

      // Start fading out in the last 30% of the animation
      if (progress > 0.7) {
        this.opacity = Math.max(0, 1 - (progress - 0.7) / 0.3);
      }
    }

    draw(ctx) {
      if (this.opacity <= 0) return;

      ctx.save();
      ctx.translate(this.x, this.y);
      ctx.rotate((this.rotation * Math.PI) / 180);
      ctx.scale(Math.cos(this.wobble), 1);
      ctx.globalAlpha = this.opacity;
      ctx.fillStyle = this.color;

      if (this.shape === 'rect') {
        ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);
      } else {
        ctx.beginPath();
        ctx.arc(0, 0, this.width / 3, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();
    }
  }

  function launchConfetti() {
    // If a canvas already exists from a previous trigger, remove it
    let existingCanvas = document.getElementById('confetti-canvas');
    if (existingCanvas) {
      existingCanvas.remove();
    }

    const canvas = document.createElement('canvas');
    canvas.id = 'confetti-canvas';
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    const particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(new Particle(canvas.width, canvas.height));
    }

    const startTime = performance.now();
    let animationFrameId = null;

    function loop(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / DURATION_MS, 1);

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < particles.length; i++) {
        particles[i].update(progress);
        particles[i].draw(ctx);
      }

      if (progress < 1) {
        animationFrameId = requestAnimationFrame(loop);
      } else {
        cleanup();
      }
    }

    function cleanup() {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      window.removeEventListener('resize', resize);
      if (canvas && canvas.parentNode) {
        canvas.parentNode.removeChild(canvas);
      }
    }

    animationFrameId = requestAnimationFrame(loop);
  }

  // Expose globally
  window.launchConfetti = launchConfetti;
})();
