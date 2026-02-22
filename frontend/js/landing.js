(function () {
  function animateScoreCircles() {
    var circles = document.querySelectorAll(".score-circle[data-score]");
    circles.forEach(function (circle) {
      var target = Number(circle.getAttribute("data-score") || 0);
      var text = circle.querySelector(".score-value") || circle.querySelector("strong");
      var current = 0;
      var step = Math.max(1, Math.ceil(target / 42));
      var timer = window.setInterval(function () {
        current += step;
        if (current >= target) {
          current = target;
          window.clearInterval(timer);
        }
        circle.style.setProperty("--score", String(current));
        if (text) text.textContent = current + "%";
      }, 24);
    });
  }

  function initReveal() {
    var nodes = document.querySelectorAll(".reveal");
    if (!nodes.length) return;

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    nodes.forEach(function (node) {
      observer.observe(node);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initReveal();
    animateScoreCircles();
  });
})();
