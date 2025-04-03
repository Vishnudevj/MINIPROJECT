// Import Supabase
const { createClient } = supabase;

// Supabase Credentials
const SUPABASE_URL = "https://mxhxbjvccaqodkycrhgk.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14aHhianZjY2Fxb2RreWNyaGdrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM1MTM0NzksImV4cCI6MjA1OTA4OTQ3OX0.nRk4hYZZlsrDYi19SPxlGoBxEeaso2JyqD7aVR97NWI";

// Initialize Supabase Client
window.supabaseClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
