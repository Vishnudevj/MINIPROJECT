document.addEventListener("DOMContentLoaded", () => {
    console.log("Register script loaded");

    const registerForm = document.getElementById("register-form");
    const errorMessage = document.getElementById("register-error");
    const successMessage = document.getElementById("register-success");

    // Ensure Supabase is loaded
    if (!window.supabaseClient) {
        console.error("Supabase is not initialized.");
        errorMessage.textContent = "Error connecting to the database.";
        return;
    }

    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Clear previous messages
        errorMessage.textContent = "";
        successMessage.textContent = "";

        // Get input values
        const name = document.getElementById("name").value.trim();
        const mobileNumber = document.getElementById("mobile-number").value.trim();
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        // Basic validation
        if (!name || !mobileNumber || !username || !password) {
            errorMessage.textContent = "All fields are required!";
            return;
        }

        if (mobileNumber.length !== 10 || isNaN(mobileNumber)) {
            errorMessage.textContent = "Enter a valid 10-digit mobile number!";
            return;
        }

        if (password.length < 6) {
            errorMessage.textContent = "Password must be at least 6 characters long!";
            return;
        }

        try {
            // Check if username already exists
            const { data: existingUser, error: fetchError } = await window.supabaseClient
                .from("User Details")  // Ensure the table name matches Supabase
                .select("Username")
                .eq("Username", username)
                .single();

            if (fetchError && fetchError.code !== "PGRST116") { // Ignore 'no rows found' error
                console.error("Error checking existing user:", fetchError);
                errorMessage.textContent = "Error checking username. Please try again.";
                return;
            }

            if (existingUser) {
                errorMessage.textContent = "Username already exists. Choose a different one!";
                return;
            }

            // Insert new user into Supabase
            const { data, error } = await window.supabaseClient
                .from("User Details")
                .insert([{ 
                    Name: name, 
                    "Mobile Number": mobileNumber, 
                    Username: username, 
                    Password: password 
                }]);

            if (error) {
                console.error("Supabase Insert Error:", error.message);
                errorMessage.textContent = `Error: ${error.message}`;
                return;
            }

            successMessage.textContent = "Registration successful! Redirecting...";
            console.log("User registered:", data);

            // Redirect to login page after 2 seconds
            setTimeout(() => window.location.href = "login.html", 2000);
        } catch (err) {
            console.error("Unexpected error:", err);
            errorMessage.textContent = "Something went wrong. Please try again!";
        }
    });
});
