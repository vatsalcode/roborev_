let robotSchedules = {
    "Franka": [],
    "Sawyer": []
};

document.getElementById('trackerForm').addEventListener('submit', (e) => {
    e.preventDefault();

    const robotName = document.getElementById('robotName').value;
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;

    if (isRobotAvailable(robotName, startTime, endTime)) {
        addReservation(robotName, startTime, endTime);
        robotSchedules[robotName].push({ startTime, endTime });
        displaySchedule(robotName);
    } else {
        alert("Robot is not available during this time.");
    }
});

function isRobotAvailable(robotName, startTime, endTime) {
    const start = convertToMinutes(startTime);
    const end = convertToMinutes(endTime);

    return robotSchedules[robotName].every(task => {
        const taskStart = convertToMinutes(task.startTime);
        const taskEnd = convertToMinutes(task.endTime);
        return end <= taskStart || start >= taskEnd;
    });
}

function convertToMinutes(time) {
    const [hours, minutes] = time.split(":").map(Number);
    return hours * 60 + minutes;
}

function displaySchedule(robotName) {
    const scheduleDisplay = document.getElementById(`${robotName}Schedule`);
    scheduleDisplay.innerHTML = '';
    robotSchedules[robotName].forEach(task => {
        const taskElement = document.createElement('div');
        taskElement.textContent = `Reserved from ${task.startTime} to ${task.endTime}`;
        scheduleDisplay.appendChild(taskElement);
    });
}

// setInterval(checkReservations, 60000);

const reservations = {
    'Franka': [],
    'Sawyer': []
};

function addReservation(robotName, startTime, endTime) {
    reservations[robotName].push({ startTime, endTime, taskStarted: false });
    updateReservationList(robotName);
}

function checkReservations() {
    const currentTime = new Date();
    for (const robot in reservations) {
        reservations[robot].forEach(res => {
            if (!res.taskStarted && isTimeToStart(currentTime, res.startTime)) {
                startProgressBar(robot, calculateDuration(res.startTime, res.endTime));
                res.taskStarted = true;
            }
        });
    }
    setTimeout(checkReservations, 60000); // Reschedule the next check
}


function isTimeToStart(currentTime, startTime) {
    const [startHours, startMinutes] = startTime.split(":").map(Number);
    return currentTime.getHours() === startHours && currentTime.getMinutes() >= startMinutes;
}

function updateReservationList(robotName) {
    const reservationList = document.getElementById(`${robotName}Reservations`);
    reservationList.innerHTML = '';
    reservations[robotName].forEach(res => {
        const listItem = document.createElement('li');
        listItem.textContent = `Reserved from ${res.startTime} to ${res.endTime}`;
        reservationList.appendChild(listItem);
    });
}

function calculateDuration(startTime, endTime) {
    const [startHours, startMinutes] = startTime.split(":").map(Number);
    const [endHours, endMinutes] = endTime.split(":").map(Number);

    const startTotalMinutes = startHours * 60 + startMinutes;
    const endTotalMinutes = endHours * 60 + endMinutes;

    return endTotalMinutes - startTotalMinutes; // Duration in minutes
}

function startProgressBar(robotName, duration) {
    document.getElementById('robotNameDisplay').textContent = `Robot Name: ${robotName}`;
    const progressBar = document.getElementById('progress');
    let elapsedSeconds = 0;
    const totalSeconds = duration * 60; // Convert duration to seconds
    const interval = setInterval(() => {
        elapsedSeconds++;
        progressBar.style.width = `${(elapsedSeconds / totalSeconds) * 100}%`;

        if (elapsedSeconds >= totalSeconds) {
            clearInterval(interval);
            document.getElementById('timeLeftDisplay').textContent = 'Time Left: Task completed';
        } else {
            const timeLeft = totalSeconds - elapsedSeconds;
            const minutesLeft = Math.floor(timeLeft / 60);
            const secondsLeft = timeLeft % 60;
            document.getElementById('timeLeftDisplay').textContent = `Time Left: ${minutesLeft}m ${secondsLeft}s`;
        }
    }, 1000); // Update every second
}
// Start the first check
setTimeout(checkReservations, 60000);

// Handle tab visibility change
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        checkReservations(); // Check immediately when the tab becomes visible
    }
});
setTimeout(checkReservations, 60000);

// Handle tab visibility change
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        checkReservations(); // Check immediately when the tab becomes visible
    }
});