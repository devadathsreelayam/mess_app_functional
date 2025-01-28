let inmate = null;

// Utility function to set button states
function setButtonState(isIn, isAblc) {
    const sgDecButton = document.getElementById('sg-dec');
    const sgIncButton = document.getElementById('sg-inc');
    const guestDecButton = document.getElementById('guest-dec');
    const guestIncButton = document.getElementById('guest-inc');

    const breakfastButton = document.getElementById('breakfast');
    const lunchButton = document.getElementById('lunch');
    const dinnerButton = document.getElementById('dinner');

    sgDecButton.disabled = isIn;
    sgIncButton.disabled = isIn;
    guestDecButton.disabled = !isIn;
    guestIncButton.disabled = !isIn;

    breakfastButton.disabled = !isIn;
    lunchButton.disabled = !isIn;
    dinnerButton.disabled = !isIn;

    if (isAblc) {
        sgDecButton.disabled = true;
        sgIncButton.disabled = true;
        guestDecButton.disabled = true;
        guestIncButton.disabled = true;
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

function toggleMealButton(mealButton, property, inmate) {
    if (inmate[property]) {
        mealButton.classList.remove('active');
        inmate[property] = false;
    } else {
        mealButton.classList.add('active');
        inmate[property] = true;
    }
}

// Function to clear and add event listeners to buttons
function addClickListeners(button, eventHandler) {
    // Clone the button to remove all previous event listeners
    const newButton = button.cloneNode(true);
    button.parentNode.replaceChild(newButton, button);

    // Add the new event listener
    newButton.addEventListener('click', eventHandler);

    return newButton; // Return the new button reference
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
                inmate = {
                    id: inmateId,
                    name: data.name,
                    department: data.department,
                    messNumber: data.mess_number,
                    status: data.status,
                    isAblc: data.is_ablc,
                    breakfast: data.breakfast,
                    lunch: data.lunch,
                    dinner: data.dinner,
                    guestCount: data.guest_count ?? 0,
                    sgCount: data.sg_count ?? 0,
                    isBillDue: data.is_bill_due
                };

                if (inmate.isBillDue) {
                    alert(`${inmate.name} has unpaid bills.\nPlease be aware!!!`);
                }

                document.querySelector('#popupName span').innerText = inmate.name;
                document.querySelector('#popupDept span').innerText = inmate.department;
                document.querySelector('#popupMessNumber span').innerText = inmate.messNumber;
                document.getElementById('popup').style.display = 'flex';

                const messStatusButton = document.getElementById('mess-status');
                messStatusButton.innerText = inmate.status === 'in' ? 'MESS IN' : 'MESS OUT';
                messStatusButton.classList.toggle('in', inmate.status === 'in');
                messStatusButton.classList.toggle('out', inmate.status === 'out');

                setButtonState(inmate.status === 'in', inmate.isAblc);

                // Toggle Mess Status
                messStatusButton.onclick = () => toggleMessStatus(messStatusButton, inmate);

                // Meal buttons
                const breakfastButton = document.getElementById('breakfast');
                const lunchButton = document.getElementById('lunch');
                const dinnerButton = document.getElementById('dinner');

                breakfastButton.classList.toggle('active', inmate.breakfast);
                lunchButton.classList.toggle('active', inmate.lunch);
                dinnerButton.classList.toggle('active', inmate.dinner);

                breakfastButton.onclick = () => toggleMealButton(breakfastButton, 'breakfast', inmate);
                lunchButton.onclick = () => toggleMealButton(lunchButton, 'lunch', inmate);
                dinnerButton.onclick = () => toggleMealButton(dinnerButton, 'dinner', inmate);

                const guestCountLabel = document.getElementById('guest-count');
                const sgCountLabel = document.getElementById('sg-count');

                guestCountLabel.innerText = inmate.guestCount;
                sgCountLabel.innerText = inmate.sgCount;

                // Increment and decrement buttons
                const guestIncButton = document.getElementById('guest-inc');
                const guestDecButton = document.getElementById('guest-dec');
                const sgIncButton = document.getElementById('sg-inc');
                const sgDecButton = document.getElementById('sg-dec');

                // Clear and add event listeners
                addClickListeners(guestIncButton, () => {
                    inmate.guestCount += 1;
                    guestCountLabel.innerText = inmate.guestCount;
                });

                addClickListeners(guestDecButton, () => {
                    if (inmate.guestCount > 0) {
                        inmate.guestCount -= 1;
                        guestCountLabel.innerText = inmate.guestCount;
                    }
                });

                addClickListeners(sgIncButton, () => {
                    if (inmate.sgCount < 3) {
                        inmate.sgCount += 1;
                        sgCountLabel.innerText = inmate.sgCount;
                    }
                });

                addClickListeners(sgDecButton, () => {
                    if (inmate.sgCount > 0) {
                        inmate.sgCount -= 1;
                        sgCountLabel.innerText = inmate.sgCount;
                    }
                });
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
    inmate = null;
    document.getElementById('popup').style.display = 'none';
});
document.getElementById('cancel').addEventListener('click', () => {
    inmate = null;
    document.getElementById('popup').style.display = 'none';
});

// Update the changes back to the database
document.getElementById('save').addEventListener('click', () => {
    const date = document.getElementById('date').value;

    if (!inmate) {
        alert('No inmate selected.');
        return;
    }

    // Collect updated data from the global inmate object
    const updatedData = {
        mess_number: inmate.messNumber,
        date: date,
        status: inmate.status,
        breakfast: inmate.breakfast ? 1 : 0,
        lunch: inmate.lunch ? 1 : 0,
        dinner: inmate.dinner ? 1 : 0,
        guest_count: inmate.guestCount,
        sg_count: inmate.sgCount
    };

    // Send the updated data to the server
    fetch('/update_inmate_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert('Changes saved successfully!');
                document.getElementById('popup').style.display = 'none';
                location.reload(); // Reload the page to reflect updates
            }
        })
        .catch(error => {
            console.error('Error saving changes:', error);
            alert('Failed to save changes.');
        });
});