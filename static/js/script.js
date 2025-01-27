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

        breakfastButton.disabled = !isIn;
        lunchButton.disabled = !isIn;
        dinnerButton.disabled = !isIn;
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
                    breakfast: data.breakfast,  // Ensure this field is correctly populated
                    lunch: data.lunch,
                    dinner: data.dinner,
                    guestCount: data.guest_count,
                    sgCount: data.sg_count,
                    isBillDue: data.is_bill_due
                };

                console.log(inmate.isBillDue);

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

                messStatusButton.addEventListener('click', () => toggleMessStatus(messStatusButton, inmate));

                const breakfastButton = document.getElementById('breakfast');
                const lunchButton = document.getElementById('lunch');
                const dinnerButton = document.getElementById('dinner');

                breakfastButton.classList.toggle('active', inmate.breakfast);
                lunchButton.classList.toggle('active', inmate.lunch);
                dinnerButton.classList.toggle('active', inmate.dinner);

                breakfastButton.addEventListener('click', () => toggleMealButton(breakfastButton, 'breakfast', inmate));
                lunchButton.addEventListener('click', () => toggleMealButton(lunchButton, 'lunch', inmate));
                dinnerButton.addEventListener('click', () => toggleMealButton(dinnerButton, 'dinner', inmate));

                const guestCountLabel = document.getElementById('guest-count');
                const sgCountLabel = document.getElementById('sg-count');

                // Setting guest and SG counts as zero if null
                inmate.guestCount = inmate.guestCount ?? 0;
                inmate.sgCount = inmate.sgCount ?? 0;

                guestCountLabel.innerText = inmate.guestCount;
                sgCountLabel.innerText = inmate.sgCount;

                const guestIncButton = document.getElementById('guest-inc');
                const guestDecButton = document.getElementById('guest-dec');
                const sgIncButton = document.getElementById('sg-inc');
                const sgDecButton = document.getElementById('sg-dec');

                guestIncButton.addEventListener('click', () => {
                    inmate.guestCount += 1;
                    guestCountLabel.innerText = inmate.guestCount;
                });
                guestDecButton.addEventListener('click', () => {
                    inmate.guestCount -= 1;
                    guestCountLabel.innerText = inmate.guestCount;
                });

                sgIncButton.addEventListener('click', () => {
                    inmate.sgCount += 1;
                    sgCountLabel.innerText = inmate.sgCount;
                });
                sgDecButton.addEventListener('click', () => {
                    inmate.sgCount -= 1;
                    sgCountLabel.innerText = inmate.sgCount;
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
    document.getElementById('popup').style.display = 'none';
});
document.getElementById('cancel').addEventListener('click', () => {
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