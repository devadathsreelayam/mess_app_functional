// Utility function to set button states
function setButtonState(isIn, isAblc) {
    const sgDecButton = document.getElementById('sg-dec');
    const sgIncButton = document.getElementById('sg-inc');
    const guestDecButton = document.getElementById('guest-dec');
    const guestIncButton = document.getElementById('guest-inc');

    if (isAblc) {
        sgDecButton.disabled = true;
        sgIncButton.disabled = true;
        guestDecButton.disabled = true;
        guestIncButton.disabled = true;
    } else {
        sgDecButton.disabled = isIn;
        sgIncButton.disabled = isIn;
        guestDecButton.disabled = !isIn;
        guestIncButton.disabled = !isIn;
    }
}

// Function to toggle mess status
function toggleMessStatus(messStatusButton, inmate) {
    if (inmate.status === 'out') {
        // Change to IN
        messStatusButton.classList.add('in');
        messStatusButton.classList.remove('out');
        messStatusButton.innerText = 'MESS IN';
        inmate.status = 'in';
    } else {
        // Change to OUT
        messStatusButton.classList.add('out');
        messStatusButton.classList.remove('in');
        messStatusButton.innerText = 'MESS OUT';
        inmate.status = 'out';
    }

    setButtonState(inmate.status === 'in', inmate.isAblc);
}

// Function to show the popup with inmate details
function showPopup(inmateId, date) {
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
                const inmate = {
                    id: inmateId,
                    name: data.name,
                    department: data.department,
                    messNumber: data.mess_number,
                    status: data.status,
                    isAblc: data.is_ablc,
                    breakfast: data.breakfast,  // Ensure this field is correctly populated
                    lunch: data.lunch,
                    dinner: data.dinner
                };

                document.querySelector('#popupName span').innerText = inmate.name;
                document.querySelector('#popupDept span').innerText = inmate.department;
                document.querySelector('#popupMessNumber span').innerText = inmate.messNumber;
                document.getElementById('popup').style.display = 'flex';

                const messStatusButton = document.getElementById('mess-status');
                messStatusButton.innerText = inmate.status === 'in' ? 'MESS IN' : 'MESS OUT';
                messStatusButton.classList.toggle('in', inmate.status === 'in');
                messStatusButton.classList.toggle('out', inmate.status === 'out');

                setButtonState(inmate.status === 'in', inmate.isAblc);

                messStatusButton.addEventListener('click', () => toggleMessStatus(messStatusButton, inmate));

                const breakfastButton = document.getElementById('breakfast');
                const lunchButton = document.getElementById('lunch');
                const dinnerButton = document.getElementById('dinner');

                breakfastButton.classList.toggle('active', inmate.breakfast);
                lunchButton.classList.toggle('active', inmate.lunch);
                dinnerButton.classList.toggle('active', inmate.dinner);
            }
        })
        .catch(error => {
            console.error('Error fetching inmate details:', error);
            alert('Error fetching inmate details.');
        });
}


// Function to handle search functionality
document.getElementById('search').addEventListener('input', function () {
    const searchTerm = this.value.toLowerCase();
    const inmates = document.querySelectorAll('.inmate-item');

    inmates.forEach(inmate => {
        const name = inmate.querySelector('.name').textContent.toLowerCase();
        const messNumber = inmate.querySelector('.mess-number').textContent.toLowerCase();

        inmate.style.display = name.includes(searchTerm) || messNumber.includes(searchTerm) ? 'grid' : 'none';
    });
});

// Shortcut to focus on search bar
document.addEventListener('keydown', function (event) {
    if (event.ctrlKey && event.key === 'f') {
        event.preventDefault();
        document.getElementById('search').focus();
    }
});

// Add event listeners to inmate items
document.querySelectorAll('.inmate-item').forEach(item => {
    item.addEventListener('click', function () {
        const inmateId = this.getAttribute('data-inmate-id');
        const date = document.getElementById('date').value;
        showPopup(inmateId, date);
    });
});

// Change date functionality
document.getElementById('date').addEventListener('change', function () {
    const selectedDate = this.value;
    if (selectedDate) {
        window.location.href = `/get_by_date/${selectedDate}`;
    }
});

// Close popup functionality
document.getElementById('closePopup').addEventListener('click', () => {
    document.getElementById('popup').style.display = 'none';
});
