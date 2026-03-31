document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const sidebar = document.querySelector("[data-sidebar]");
    const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
    const sidebarClose = document.querySelector("[data-sidebar-close]");
    const sidebarOverlay = document.querySelector("[data-sidebar-overlay]");

    const closeSidebar = () => {
        if (!sidebar) {
            return;
        }
        sidebar.classList.remove("is-open");
        body.classList.remove("sidebar-open");
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove("is-visible");
        }
        if (sidebarToggle) {
            sidebarToggle.setAttribute("aria-expanded", "false");
        }
    };

    const openSidebar = () => {
        if (!sidebar) {
            return;
        }
        sidebar.classList.add("is-open");
        body.classList.add("sidebar-open");
        if (sidebarOverlay) {
            sidebarOverlay.classList.add("is-visible");
        }
        if (sidebarToggle) {
            sidebarToggle.setAttribute("aria-expanded", "true");
        }
    };

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", () => {
            const isOpen = sidebar?.classList.contains("is-open");
            if (isOpen) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (sidebarClose) {
        sidebarClose.addEventListener("click", closeSidebar);
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener("click", closeSidebar);
    }

    window.addEventListener("resize", () => {
        if (window.innerWidth > 1023) {
            closeSidebar();
        }
    });

    const animatedNodes = document.querySelectorAll("[data-animate]");
    animatedNodes.forEach((node, index) => {
        node.style.setProperty("--delay", `${index * 70}ms`);
    });

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.14 });

        animatedNodes.forEach((node) => observer.observe(node));
    } else {
        animatedNodes.forEach((node) => node.classList.add("is-visible"));
    }

    document.querySelectorAll(".score-ring[data-score]").forEach((ring) => {
        const rawScore = Number.parseInt(ring.getAttribute("data-score") || "0", 10);
        const score = Number.isNaN(rawScore) ? 0 : Math.max(0, Math.min(100, rawScore));
        ring.style.setProperty("--score", score);
    });

    document.querySelectorAll(".resume-score-meter[data-progress]").forEach((meter) => {
        const rawProgress = Number.parseInt(meter.getAttribute("data-progress") || "0", 10);
        const progress = Number.isNaN(rawProgress) ? 0 : Math.max(0, Math.min(100, rawProgress));
        const fill = meter.querySelector("[data-progress-fill]");
        const valueNode = meter.querySelector("[data-progress-value]");

        requestAnimationFrame(() => {
            if (fill) {
                fill.style.width = `${progress}%`;
            }
        });

        if (valueNode) {
            let current = 0;
            const duration = 900;
            const start = performance.now();

            const animateValue = (now) => {
                const elapsed = now - start;
                const ratio = Math.min(elapsed / duration, 1);
                current = Math.round(progress * ratio);
                valueNode.textContent = `${current}%`;
                if (ratio < 1) {
                    requestAnimationFrame(animateValue);
                }
            };

            requestAnimationFrame(animateValue);
        }
    });

    const fileInput = document.querySelector("[data-file-input]");
    const fileNameNode = document.querySelector("[data-file-name]");
    if (fileInput && fileNameNode) {
        fileInput.addEventListener("change", () => {
            const selectedFile = fileInput.files && fileInput.files.length > 0 ? fileInput.files[0].name : "No file selected yet";
            fileNameNode.textContent = selectedFile;
        });
    }

    const chartCanvas = document.getElementById("adminGrowthChart");
    if (chartCanvas && window.Chart) {
        const labelsNode = document.getElementById("chart-labels");
        const usersNode = document.getElementById("chart-users");
        const jobsNode = document.getElementById("chart-jobs");
        const applicationsNode = document.getElementById("chart-applications");

        const labels = labelsNode ? JSON.parse(labelsNode.textContent) : [];
        const users = usersNode ? JSON.parse(usersNode.textContent) : [];
        const jobs = jobsNode ? JSON.parse(jobsNode.textContent) : [];
        const applications = applicationsNode ? JSON.parse(applicationsNode.textContent) : [];

        new Chart(chartCanvas, {
            type: "line",
            data: {
                labels,
                datasets: [
                    {
                        label: "Users",
                        data: users,
                        borderColor: "#2563eb",
                        backgroundColor: "rgba(37, 99, 235, 0.12)",
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 5,
                    },
                    {
                        label: "Jobs",
                        data: jobs,
                        borderColor: "#60a5fa",
                        backgroundColor: "rgba(96, 165, 250, 0.08)",
                        borderWidth: 3,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 4,
                        pointHoverRadius: 5,
                    },
                    {
                        label: "Applications",
                        data: applications,
                        borderColor: "#0f9f6e",
                        backgroundColor: "rgba(15, 159, 110, 0.1)",
                        borderWidth: 3,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 4,
                        pointHoverRadius: 5,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "index",
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: "top",
                        align: "end",
                        labels: {
                            usePointStyle: true,
                            boxWidth: 10,
                            color: "#4f6178",
                            padding: 18,
                        },
                    },
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                        },
                        ticks: {
                            color: "#7b8ca3",
                        },
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: "rgba(200, 214, 234, 0.45)",
                        },
                        ticks: {
                            precision: 0,
                            color: "#7b8ca3",
                        },
                    },
                },
            },
        });
    }

    const candidateChartCanvas = document.getElementById("candidateOverviewChart");
    if (candidateChartCanvas && window.Chart) {
        const labelsNode = document.getElementById("candidate-chart-labels");
        const valuesNode = document.getElementById("candidate-chart-values");
        const labels = labelsNode ? JSON.parse(labelsNode.textContent) : [];
        const values = valuesNode ? JSON.parse(valuesNode.textContent) : [];

        new Chart(candidateChartCanvas, {
            type: "bar",
            data: {
                labels,
                datasets: [
                    {
                        label: "Candidate Activity",
                        data: values,
                        backgroundColor: ["#2563eb", "#60a5fa", "#0f9f6e"],
                        borderRadius: 14,
                        borderSkipped: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                        },
                        ticks: {
                            color: "#7b8ca3",
                        },
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                            color: "#7b8ca3",
                        },
                        grid: {
                            color: "rgba(200, 214, 234, 0.45)",
                        },
                    },
                },
            },
        });
    }
});
