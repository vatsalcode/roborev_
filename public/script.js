document.getElementById('trackerForm').addEventListener('submit', (e) => {
    e.preventDefault();

    const robotName = document.getElementById('robotName').value;
    const task = document.getElementById('task').value;
    const time = document.getElementById('time').value;

    console.log(`Robot: ${robotName}, Task: ${task}, Time: ${time} hours`);
    // Here, you can send this data to the server or handle it as needed
});
