const today = new Date().toISOString().split('T')[0];
document.getElementById("date").value = today;

// Add event listener to the search bar
document.getElementById("search").addEventListener("input", function() {
    const searchTerm = this.value.toLowerCase(); // Get the search term and convert to lowercase
    const inmates = document.querySelectorAll(".inmate-item"); // Select all inmate-item divs

    inmates.forEach((inmate) => {
        const name = inmate.querySelector(".name").textContent.toLowerCase(); // Get name text
        const messNumber = inmate.querySelector(".mess-number").textContent.toLowerCase(); // Get mess number text

        // Check if the search term matches either name or mess number
        if (name.includes(searchTerm) || messNumber.includes(searchTerm)) {
            inmate.style.display = "grid"; // Show the matching inmate
        } else {
            inmate.style.display = "none"; // Hide the non-matching inmate
        }
    });
});

document.addEventListener("keydown", function(event) {
    // Check if the Ctrl key and F key are pressed simultaneously
    if (event.ctrlKey && event.key === "f") {
        event.preventDefault(); // Prevent the default browser find behavior
        document.getElementById("search").focus(); // Set focus to the search bar
    }
});