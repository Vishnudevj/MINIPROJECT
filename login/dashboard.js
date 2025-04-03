console.log("Dashboard script loaded");

// Wait for Supabase to initialize
document.addEventListener("DOMContentLoaded", async () => {
    console.log("Checking Supabase initialization...");

    if (!window.supabaseClient) {
        console.error("Supabase is not initialized. Please check supabase.js.");
        return;
    }

    console.log("Supabase is initialized successfully.");
    showSection("user-history"); // Default section
});

// Function to fetch user history
async function fetchUserHistory(userDataString) {
    if (!window.supabaseClient) {
        console.error("Supabase is not initialized.");
        return;
    }

    try {
        const userData = JSON.parse(userDataString);
        console.log("Fetching user history for:", userData.Username);

        // Fetch user details (Name, Mobile Number)
        const { data: userDetails, error: userError } = await window.supabaseClient
            .from("User Details")
            .select("Name, \"Mobile Number\"")  
            .eq("Username", userData.Username)
            .single();

        if (userError) throw userError;
        console.log("User details fetched:", userDetails);

        // Fetch alert history (Alert Type, Time)
        const { data: alertHistory, error: alertError } = await window.supabaseClient
            .from("Alert History")
            .select("\"Alert Type\", Time")  
            .eq("Username", userData.Username);

        if (alertError) throw alertError;
        console.log("Alert history fetched:", alertHistory);

        // Update UI
        const historyContent = document.getElementById("history-content");
        historyContent.innerHTML = `
            <p><strong>Name:</strong> ${userDetails.Name}</p>
            <p><strong>Mobile Number:</strong> ${userDetails["Mobile Number"]}</p>
            <h4>Alert History:</h4>
            <ul>
                ${alertHistory.length > 0 
                    ? alertHistory.map(alert => {
                        const formattedTime = new Date(alert.Time).toLocaleString();
                        return `<li>${alert["Alert Type"]} - ${formattedTime}</li>`;
                    }).join("")
                    : "<li>No alerts found.</li>"
                }
            </ul>
        `;

    } catch (error) {
        console.error("Error fetching user history:", error);
        document.getElementById("history-content").innerHTML = "<p style='color: red;'>Error loading user history.</p>";
    }
}

// Function to fetch and plot alert history as a Histogram (Frequency vs Time)
async function fetchAndPlotHistogram(userDataString) {
    if (!window.supabaseClient) {
        console.error("Supabase is not initialized.");
        return;
    }

    try {
        const userData = JSON.parse(userDataString);
        console.log("Fetching alert history for:", userData.Username);

        // Fetch alert history (Time)
        const { data: alertHistory, error: alertError } = await window.supabaseClient
            .from("Alert History")
            .select("Time")  
            .eq("Username", userData.Username);

        if (alertError) throw alertError;
        console.log("Alert history fetched:", alertHistory);

        if (alertHistory.length === 0) {
            console.warn("No alerts found for the user.");
            return;
        }

        // Process data for Histogram (Group alerts by 30-minute intervals)
        const timeBins = {}; 
        const intervalMinutes = 30; 

        alertHistory.forEach(alert => {
            const alertTime = new Date(alert.Time);
            const roundedMinutes = Math.floor(alertTime.getMinutes() / intervalMinutes) * intervalMinutes;
            const binKey = `${alertTime.getFullYear()}-${alertTime.getMonth() + 1}-${alertTime.getDate()} ${alertTime.getHours()}:${roundedMinutes}`;

            if (!timeBins[binKey]) {
                timeBins[binKey] = 0;
            }
            timeBins[binKey]++;
        });

        // Extract data for the chart
        const labels = Object.keys(timeBins).sort();  
        const data = labels.map(key => timeBins[key]);

        // Create or update the histogram chart
        const ctx = document.getElementById("alertHistogram").getContext("2d");

        if (window.alertHistogramInstance) {
            window.alertHistogramInstance.destroy();  // Destroy existing chart before re-drawing
        }

        window.alertHistogramInstance = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Alert Frequency",
                    data: data,
                    backgroundColor: "rgba(75, 192, 192, 0.6)",
                    borderColor: "rgba(75, 192, 192, 1)",
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: { display: true, text: "Time (Grouped in 30 min intervals)" },
                        ticks: { maxRotation: 45, minRotation: 45, autoSkip: true }
                    },
                    y: {
                        title: { display: true, text: "Alert Count" },
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1, 
                            callback: function(value) {
                                return Number.isInteger(value) ? value : ""; 
                            }
                        }
                    }
                },
                plugins: {
                    legend: { display: false }, 
                    tooltip: { enabled: true }
                }
            }
        });

    } catch (error) {
        console.error("Error fetching and plotting alert history:", error);
        document.getElementById("analytics").innerHTML = "<p style='color: red;'>Error loading alert analytics.</p>";
    }
}

// Function to load live video feed
function loadLiveFeed() {
    const liveFeed = document.getElementById("liveFeed");
    liveFeed.src = "http://127.0.0.1:5000/video_feed"; 
}

// Function to switch dashboard sections
function showSection(section) {
    const sections = ["user-history", "analytics", "video-feed"];
    sections.forEach(sectionId => document.getElementById(sectionId).classList.add("hidden"));

    document.getElementById(section).classList.remove("hidden");

    if (section === "user-history") {
        const userDataString = localStorage.getItem("loggedInUser");
        if (userDataString) {
            fetchUserHistory(userDataString);
        } else {
            window.location.href = "login.html";
        }
    } else if (section === "analytics") {
        const userDataString = localStorage.getItem("loggedInUser");
        if (userDataString) {
            fetchAndPlotHistogram(userDataString);
        }
    } else if (section === "video-feed") {
        loadLiveFeed();
    }
}

// Logout function
function logout() {
    localStorage.removeItem("loggedInUser");
    window.location.href = "login.html";
}
