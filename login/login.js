document.addEventListener("DOMContentLoaded", () => {
    console.log("Login script loaded");

    const loginForm = document.getElementById("login-form");
    const errorMessage = document.getElementById("login-error");

    // Ensure Supabase is loaded
    if (!window.supabaseClient) {
        console.error("Supabase is not initialized.");
        errorMessage.textContent = "Error connecting to the database.";
        return;
    }

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Clear any previous error messages
        errorMessage.textContent = "";

        // Get the username and password entered by the user
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        // Basic validation
        if (!username || !password) {
            errorMessage.textContent = "Please enter both username and password.";
            return;
        }

        try {
            // Query Supabase for a user with the entered username
            const { data, error } = await window.supabaseClient
                .from("User Details")
                .select("Username, Password")
                .eq("Username", username)
                .single();  // Fetch a single user

            if (error) {
                console.error("Error fetching user details:", error.message);
                errorMessage.textContent = "An error occurred. Please try again.";
                return;
            }

            // If user found, check if the password matches
            if (data && data.Password === password) {
                console.log("Login successful! Redirecting...");
                // Store user data in localStorage for session persistence
                localStorage.setItem("loggedInUser", JSON.stringify(data));

                // Redirect to dashboard page
                window.location.href = "dashboard.html";
            } else {
                // Invalid username or password
                errorMessage.textContent = "Invalid username or password.";
            }
        } catch (err) {
            console.error("Unexpected error:", err);
            errorMessage.textContent = "Something went wrong. Please try again.";
        }
    });
});
