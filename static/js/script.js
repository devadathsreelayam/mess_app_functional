var messInStatus; // in or out

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


// Popup functionality
// Function to show the popup with inmate details
function showPopup(inmateId) {
    const date = document.getElementById('date').value;

    if (!date) {
        alert('Please select date.');
        return;
    }

    fetch(`/get_inmate_details/${inmateId}?date=${date}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                document.querySelector('#popupName span').innerText = data.name;
                document.querySelector('#popupDept span').innerText = data.department;
                document.querySelector('#popupMessNumber span').innerText = data.mess_number;
                document.getElementById('popup').style.display = 'flex';

                // Alter the global status variable
                messInStatus = data.status;

                if (data.status == 'in') {
                    // Change the status button to in
                    const messStatusButton = document.getElementById('mess-status');
                    messStatusButton.innerText = 'MESS IN';
                    messStatusButton.classList.remove('out');
                    messStatusButton.classList.add('in');

                    // Disable the SG button when inmate is IN
                    document.getElementById('sg-dec').disabled = true;
                    document.getElementById('sg-inc').disabled = true;

                    // Enable the GUEST button when inmate is IN
                    document.getElementById('guest-dec').disabled = false;
                    document.getElementById('guest-inc').disabled = false;
                } else {
                    // Change the status button to out
                    const messStatusButton = document.getElementById('mess-status');
                    messStatusButton.innerText = 'MESS IN';
                    messStatusButton.classList.add('out');
                    messStatusButton.classList.remove('in');

                    // Enable the SG button when inmate is OUT
                    document.getElementById('sg-dec').disabled = false;
                    document.getElementById('sg-inc').disabled = false;

                    // Disable the GUEST button when inmate is OUT
                    document.getElementById('guest-dec').disabled = true;
                    document.getElementById('guest-inc').disabled = true;
                }

                // Disable SG and GUEST for ABLC inmates
                if (data.is_ablc == true) {
                    // Disable the GUEST button
                    document.getElementById('guest-dec').disabled = true;
                    document.getElementById('guest-inc').disabled = true;

                    // Disable the SG button
                    document.getElementById('sg-dec').disabled = true;
                    document.getElementById('sg-inc').disabled = true;
                }
            }
        });
}

// Close the popup
document.getElementById('closePopup').addEventListener('click', () => {
    document.getElementById('popup').style.display = 'none';
});

// Add event listeners to each inmate-item
document.querySelectorAll('.inmate-item').forEach(item => {
    item.addEventListener('click', function() {
        const inmateId = this.getAttribute('data-inmate-id');
        showPopup(inmateId);
    });
});


// Change date
document.getElementById('date').addEventListener('change', function () {
    const selectedDate = this.value; // Get the selected date from the input

    if (selectedDate) {
        // Construct the new URL
        const newUrl = `/get_by_date/${selectedDate}`;

        // Update the URL and reload the page with new data
        window.location.href = newUrl;
    }
});